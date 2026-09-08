"""Estado vivo del Bot: navegador, sesión SIIF y la corrida en curso.

Solo puede haber un navegador y una sesión SIIF a la vez, así que `_busy`
serializa toda operación que toque Selenium. Los comandos cortos (login,
logout) se ejecutan y responden; `execute` arranca un hilo y responde de
inmediato, informando su avance por eventos.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable

import protocol
from core import ChromeDriver
from services.workflows.orchestrator import Orchestrator

Emitter = Callable[[str, dict], None]


class BotBusyError(Exception):
    """Ya hay una operación de Selenium en curso."""


class BotSession:
    def __init__(self, emit: Emitter):
        self._emit = emit
        self._busy = threading.Lock()
        self._chrome: ChromeDriver | None = None
        self._orchestrator: Orchestrator | None = None
        self._stop_event = threading.Event()
        self._worker: threading.Thread | None = None

        self.username = ""
        self.logged_in = False
        self.running = False
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
            "driver_activo": self._chrome is not None,
            "progress": dict(self.progress),
            "counters": dict(self.counters),
            "last_summary": self.last_summary,
        }

    def _emit_state(self) -> None:
        self._emit(protocol.EVT_STATE, self.snapshot())

    def _track(self, event: str, payload: dict[str, Any]) -> None:
        """Actualiza el estado interno con cada evento del orquestador."""
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
        if not self._busy.acquire(blocking=False):
            raise BotBusyError("El bot está ocupado con otra operación")
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
            if not ok:
                self._close_browser()
            self._emit_state()
            return ok, message
        except Exception as exc:
            logging.exception("Error en login")
            self._close_browser()
            self.logged_in = False
            self._emit_state()
            return False, f"Error abriendo la sesión: {exc}"
        finally:
            self._busy.release()

    def execute(self) -> tuple[bool, str]:
        """Arranca el lote en un hilo y responde de inmediato."""
        if not self.logged_in or self._orchestrator is None:
            return False, "No hay sesión activa en SIIF. Inicia sesión primero."
        if not self._busy.acquire(blocking=False):
            raise BotBusyError("Ya hay un proceso en ejecución")

        self._stop_event.clear()
        self.running = True
        self._emit_state()

        self._worker = threading.Thread(target=self._run_batch, name="bot-batch", daemon=True)
        self._worker.start()
        return True, "Proceso iniciado"

    def _run_batch(self) -> None:
        try:
            assert self._orchestrator is not None
            self._orchestrator.run_batch()
        except Exception as exc:
            logging.exception("Error ejecutando el lote")
            self._emit(
                protocol.EVT_LOG, {"level": "error", "message": f"Error en el lote: {exc}"}
            )
            self._emit(
                protocol.EVT_RUN_FINISHED,
                {"error": str(exc), **dict(self.counters), "detenido": True},
            )
        finally:
            self.running = False
            self._busy.release()
            self._emit_state()

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
