"""Estado vivo del Bot: navegador, sesión SIIF y la corrida en curso.

Solo puede haber un navegador y una sesión SIIF a la vez, así que `_busy`
serializa toda operación que toque Selenium. Los comandos cortos (login,
logout) se ejecutan y responden; las corridas (lote, consulta y demo) arrancan un
hilo y responden de inmediato, informando su avance por eventos.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable

import protocol
from core import ChromeDriver
from services.data.cuentas import MAX_CUENTAS_POR_CONSULTA, limpiar_cuentas
from services.observers import EventObserver, RunNotifier, TraceObserver
from services.workflows.orchestrator import Orchestrator

Emitter = Callable[[str, dict], None]

SIN_SESION = "No hay sesión activa en SIIF. Inicia sesión primero."


class BotBusyError(Exception):
    """Ya hay una operación de Selenium en curso."""


class BotSession:
    def __init__(self, emit: Emitter):
        self._emit = emit
        self._busy = threading.Lock()
        self._chrome: ChromeDriver | None = None
        self._orchestrator: Orchestrator | None = None
        self._stop_event = threading.Event()

        self.username = ""
        self.logged_in = False
        self.running = False
        self.connecting = False
        self.last_message = ""
        self.progress: dict[str, Any] = {"current": 0, "total": 0, "numero_cuenta": ""}
        self.counters: dict[str, int] = {"exitos": 0, "errores": 0}
        self.last_summary: dict[str, Any] | None = None

    # --- estado -----------------------------------------------------------
    def snapshot(self) -> dict[str, Any]:
        """Retrato del estado actual, que la UI usa para pintarse."""
        return {
            "username": self.username,
            "logged_in": self.logged_in,
            "running": self.running,
            "connecting": self.connecting,
            "last_message": self.last_message,
            "driver_activo": self._chrome is not None,
            "progress": dict(self.progress),
            "counters": dict(self.counters),
            "last_summary": self.last_summary,
        }

    def _emit_state(self) -> None:
        self._emit(protocol.EVT_STATE, self.snapshot())

    def _track(self, event: str, payload: dict[str, Any]) -> None:
        """Actualiza el estado interno con cada evento de la corrida."""
        if event == protocol.EVT_RUN_STARTED:
            self.progress = {
                "current": 0,
                "total": payload.get("total", 0),
                "numero_cuenta": "",
            }
            self.counters = {"exitos": 0, "errores": 0}
        elif event == protocol.EVT_PROGRESS:
            self.progress = {
                "current": payload.get("current", 0),
                "total": payload.get("total", 0),
                "numero_cuenta": payload.get("numero_cuenta", ""),
            }
        elif event == protocol.EVT_RECORD:
            key = "exitos" if payload.get("ok") else "errores"
            self.counters[key] += 1
        elif event == protocol.EVT_RUN_FINISHED:
            self.last_summary = payload

        self._emit(event, payload)

    # --- comandos que tocan Selenium --------------------------------------
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Arranca el login en un hilo y responde de inmediato.

        Abrir Chrome y esperar a SIIF puede tardar minutos (DEFAULT_LOGIN_TIMEOUT);
        si respondiéramos solo al final, el cliente se rendiría antes por timeout.
        El resultado llega por eventos de estado.
        """
        if not self._busy.acquire(blocking=False):
            raise BotBusyError("El bot está ocupado con otra operación")

        self.connecting = True
        self.last_message = ""
        self._emit_state()

        threading.Thread(
            target=self._do_login, args=(username, password), name="bot-login", daemon=True
        ).start()
        return True, "Abriendo Chrome e iniciando sesión en SIIF..."

    def _do_login(self, username: str, password: str) -> None:
        try:
            self.logout(_already_locked=True)

            self._emit(protocol.EVT_LOG, {"level": "info", "message": "Abriendo Chrome"})
            self._chrome = ChromeDriver()
            driver = self._chrome.create_driver()
            self._orchestrator = Orchestrator(
                driver, on_event=self._track, stop_event=self._stop_event
            )

            ok, message = self._orchestrator.login(username, password)
            self.logged_in = ok
            self.username = username if ok else ""
            self.last_message = message
            if not ok:
                self._close_browser()
        except Exception as exc:
            logging.exception("Error en login")
            self._close_browser()
            self.logged_in = False
            self.last_message = f"Error abriendo la sesión: {exc}"
            self._emit(
                protocol.EVT_LOG, {"level": "error", "message": self.last_message}
            )
        finally:
            self.connecting = False
            self._busy.release()
            self._emit_state()

    def execute(self) -> tuple[bool, str]:
        """Lote desde ENTRADAS.xlsx, en segundo plano."""
        if not self.logged_in or self._orchestrator is None:
            return False, SIN_SESION
        self._lanzar(self._orchestrator.run_batch, "bot-batch")
        return True, "Proceso iniciado"

    def consultar(self, cuentas: Any) -> tuple[bool, str]:
        """Consulta en SIIF las cuentas escritas en la UI, en segundo plano."""
        if not self.logged_in or self._orchestrator is None:
            return False, SIN_SESION
        validas, error = self._validar_cuentas(cuentas)
        if error:
            return False, error
        orchestrator = self._orchestrator
        self._lanzar(lambda: orchestrator.run_consulta(validas), "bot-consulta")
        return True, f"Consultando {len(validas)} cuenta(s) en SIIF"

    @staticmethod
    def _validar_cuentas(cuentas: Any) -> tuple[list[str], str | None]:
        """El Bot valida por su cuenta: no puede fiarse de lo que llegue por el socket."""
        validas, invalidas = limpiar_cuentas(cuentas or [])
        if invalidas:
            return [], "Números de cuenta no válidos (solo dígitos): " + ", ".join(invalidas[:5])
        if not validas:
            return [], "Escribe al menos un número de cuenta"
        if len(validas) > MAX_CUENTAS_POR_CONSULTA:
            return [], (
                f"Máximo {MAX_CUENTAS_POR_CONSULTA} cuentas por consulta; "
                "para más, usa el lote desde ENTRADAS.xlsx"
            )
        return validas, None

    def _lanzar(self, trabajo: Callable[[], Any], nombre: str) -> None:
        if not self._busy.acquire(blocking=False):
            raise BotBusyError("Ya hay un proceso en ejecución")
        self._stop_event.clear()
        self.running = True
        self._emit_state()
        threading.Thread(target=self._trabajar, args=(trabajo,), name=nombre, daemon=True).start()

    def _trabajar(self, trabajo: Callable[[], Any]) -> None:
        try:
            trabajo()
        except Exception as exc:
            # La corrida ya se cerró (trazabilidad y resumen) en su propio finally.
            logging.exception("Error ejecutando el proceso")
            self._emit(
                protocol.EVT_LOG, {"level": "error", "message": f"Error en el proceso: {exc}"}
            )
        finally:
            self.running = False
            self._busy.release()
            self._emit_state()

    def demo(
        self, registros: int = 12, pausa: float = 1.0, cuentas: Any = None
    ) -> tuple[bool, str]:
        """Recorre un lote falso emitiendo los mismos eventos que una corrida real.

        No abre Chrome ni toca SIIF: sirve para ver y desarrollar la UI sin gastar
        una sesión del sistema real. Si llegan cuentas escritas en la UI, simula
        consultarlas a ellas en vez de generar registros. Usa el mismo lock y la
        misma bandera de parada, así que el botón Detener funciona igual.
        """
        validas: list[str] = []
        if cuentas:
            validas, error = self._validar_cuentas(cuentas)
            if error:
                return False, error
        self._lanzar(lambda: self._run_demo(registros, pausa, validas), "bot-demo")
        return True, f"Demo iniciada: {len(validas) or registros} registros simulados"

    def _run_demo(self, registros: int, pausa: float, cuentas: list[str]) -> None:
        # Mismos observadores que una corrida real salvo los Excel de negocio:
        # la demo deja trazabilidad (marcada como demo) pero no toca CONCILIACION.
        filas = cuentas or [f"0010021{i:010d}" for i in range(1, registros + 1)]
        notifier = RunNotifier(
            [TraceObserver(), EventObserver(self._track)],
            modo="demo",
            origen="ui" if cuentas else "lote",
            usuario=self.username or "demo",
        )
        detenido = False
        error: str | None = None
        try:
            self._emit(
                protocol.EVT_LOG,
                {"level": "info", "message": "Modo demo: no se abre Chrome ni se toca SIIF"},
            )
            notifier.start(len(filas))

            for i, cuenta in enumerate(filas, start=1):
                if self._stop_event.is_set():
                    detenido = True
                    self._emit(
                        protocol.EVT_LOG,
                        {"level": "warning", "message": "Demo detenida por el usuario"},
                    )
                    break

                entrada = {"INDEX": str(i), "NUMERO_CUENTA": cuenta}
                notifier.begin_record(i, entrada)
                time.sleep(pausa)

                ok = i % 4 != 0  # uno de cada cuatro falla, para ver ambos caminos
                notifier.record(
                    i,
                    entrada,
                    ok,
                    "Simulado correctamente" if ok else "Cuenta no encontrada (simulado)",
                    {"NOMBRE_CUENTA": f"CLIENTE DE PRUEBA {i}"} if ok else {},
                )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            logging.exception("Error en la demo")
        finally:
            notifier.finish(detenido=detenido, error=error)

    def request_stop(self) -> tuple[bool, str]:
        """No toma el lock: debe poder llamarse mientras el lote corre."""
        if not self.running:
            return False, "No hay ningún proceso en ejecución"
        self._stop_event.set()
        self._emit(
            protocol.EVT_LOG,
            {"level": "warning", "message": "Detención solicitada, terminando el registro actual"},
        )
        return True, "Detención solicitada"

    def logout(self, _already_locked: bool = False) -> tuple[bool, str]:
        if not _already_locked and not self._busy.acquire(blocking=False):
            raise BotBusyError("El bot está ocupado con otra operación")
        try:
            self._close_browser()
            self.logged_in = False
            self.username = ""
            if not _already_locked:
                self._emit_state()
            return True, "Sesión cerrada"
        finally:
            if not _already_locked:
                self._busy.release()

    def _close_browser(self) -> None:
        if self._chrome is not None:
            try:
                self._chrome.quit_driver()
            except Exception:
                logging.warning("No se pudo cerrar Chrome limpiamente", exc_info=True)
        self._chrome = None
        self._orchestrator = None
