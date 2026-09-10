import logging
import threading
from typing import Any, Callable

import protocol
from config.settings import BATCH_SIZE, SIIF_URL
from core.base import BasePage
from core.utils.errores import mensaje_legible
from services.data.data_manager import DataManager
from services.observers import RunNotifier, observadores_por_defecto
from services.processes.login_siif import SIIFLoginProcess
from services.processes.search_account_name import SearchAccountName


class Orchestrator:
    """Coordina el proceso completo sobre un driver ya creado.

    No sabe nada de WebSockets ni de Streamlit. Es el sujeto del patrón Observer:
    avisa a los observadores de la corrida (trazabilidad, Excel de negocio y
    eventos para la UI) y revisa `stop_event` entre registros para poder cancelar.
    """

    def __init__(
        self,
        driver,
        on_event: Callable[[str, dict], None] | None = None,
        stop_event: threading.Event | None = None,
    ):
        self.driver = driver
        self.page = BasePage(driver)
        self.data_manager = DataManager()
        self.username = ""
        self._on_event = on_event or (lambda *_args, **_kwargs: None)
        self._stop_event = stop_event or threading.Event()

    def _log(self, message: str, level: str = "info") -> None:
        getattr(logging, level, logging.info)(message)
        self._on_event(protocol.EVT_LOG, {"level": level, "message": message})

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Navega a SIIF y autentica. Deja la sesión abierta para las corridas."""
        self._log(f"Navegando a {SIIF_URL}")
        self.page.navigate_to(SIIF_URL)

        is_login, message = SIIFLoginProcess(self.page).execute(username, password)
        self._log(message, "info" if is_login else "error")
        if is_login:
            self.username = username
        return is_login, message

    def run_batch(self) -> dict[str, Any]:
        """Lote desde ENTRADAS.xlsx: trazabilidad, Excel de negocio y retirada de
        cada fila de la entrada una vez registrada."""
        return self._run(
            lambda: self.data_manager.load_input().to_dicts(),
            origen="lote",
            con_excel=True,
            retirar_de_entrada=True,
        )

    def run_consulta(self, cuentas: list[str]) -> dict[str, Any]:
        """Cuentas escritas en la UI. Quedan en la trazabilidad, pero no tocan
        ENTRADAS.xlsx ni los Excel de negocio: una consulta suelta pisaría la
        conciliación del último lote."""
        filas = [
            {"INDEX": str(i), "NUMERO_CUENTA": cuenta} for i, cuenta in enumerate(cuentas, start=1)
        ]
        return self._run(lambda: filas, origen="ui", con_excel=False, retirar_de_entrada=False)

    def _run(
        self,
        cargar_filas: Callable[[], list[dict[str, Any]]],
        *,
        origen: str,
        con_excel: bool,
        retirar_de_entrada: bool,
    ) -> dict[str, Any]:
        """Recorre las filas con el proceso de la plantilla, avisando a los observadores.

        Cada resultado queda escrito en la trazabilidad antes de pasar al siguiente,
        y solo entonces se retira de la entrada. La corrida se cierra en un
        `finally`: completa, detenida o con error, siempre deja su resumen.
        """
        notifier = RunNotifier(
            observadores_por_defecto(self._on_event, con_excel=con_excel),
            usuario=self.username,
            origen=origen,
        )
        detenido = False
        error: str | None = None
        pendientes: list = []
        try:
            rows = cargar_filas()
            notifier.start(len(rows))
            self._log(f"Corrida {notifier.run.run_id} ({origen}): {len(rows)} registros por procesar")
            searcher = SearchAccountName(self.driver)

            for posicion, row in enumerate(rows, start=1):
                if self._stop_event.is_set():
                    detenido = True
                    self._log("Detención solicitada: se interrumpe el lote", "warning")
                    break

                notifier.begin_record(posicion, row)
                # El proceso se reutiliza entre registros: sin limpiar, un fallo
                # heredaría el NOMBRE_CUENTA del registro anterior.
                searcher.clear_variables()
                try:
                    ok, mensaje = searcher.execute(**row)
                except Exception as exc:
                    # Queda registrado, pero no se retira de la entrada: se reintentará.
                    notifier.record(
                        posicion,
                        row,
                        False,
                        f"Error inesperado: {mensaje_legible(exc)}",
                        searcher.get_variables(),
                    )
                    raise
                notifier.record(posicion, row, ok, mensaje, searcher.get_variables())

                if retirar_de_entrada:
                    pendientes.append(row["INDEX"])
                    if len(pendientes) >= BATCH_SIZE:
                        pendientes = self._retirar_de_entrada(pendientes)
        except Exception as exc:
            error = mensaje_legible(exc)
            raise
        finally:
            self._retirar_de_entrada(pendientes)
            summary = notifier.finish(detenido=detenido, error=error)
            self._log(
                f"Corrida {summary['run_id']} cerrada. Éxitos: {summary['exitos']}, "
                f"errores: {summary['errores']}"
                + (" (detenida por el usuario)" if detenido else "")
                + (f" (error: {error})" if error else ""),
                "error" if error else "info",
            )
        return summary

    def _retirar_de_entrada(self, ids: list) -> list:
        """Quita de ENTRADAS.xlsx registros cuyo resultado ya está en la trazabilidad.

        Si falla (por ejemplo, el Excel está abierto) no tira la corrida: devuelve
        los ids para reintentarlo con el siguiente lote.
        """
        if not ids:
            return []
        try:
            self.data_manager.update_entries(ids)
            return []
        except Exception as exc:
            self._log(
                f"No se pudo actualizar la entrada ({mensaje_legible(exc)}); se reintentará",
                "warning",
            )
            return ids
