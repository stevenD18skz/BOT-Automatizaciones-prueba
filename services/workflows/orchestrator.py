import logging
import threading
from typing import Any, Callable

import protocol
from config.settings import BATCH_SIZE, SIIF_URL
from core.base import BasePage
from services.data.data_manager import DataManager
from services.processes.login_siif import SIIFLoginProcess
from services.processes.search_account_name import SearchAccountName


class Orchestrator:
    """Coordina el proceso completo sobre un driver ya creado.

    No sabe nada de WebSockets ni de Streamlit: informa su avance llamando a
    `on_event(nombre, payload)` y revisa `stop_event` entre registros para poder
    cancelar a mitad de un lote.
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
        self._on_event = on_event or (lambda *_args, **_kwargs: None)
        self._stop_event = stop_event or threading.Event()

    def _emit(self, event: str, payload: dict[str, Any] | None = None) -> None:
        self._on_event(event, payload or {})

    def _log(self, message: str, level: str = "info") -> None:
        getattr(logging, level, logging.info)(message)
        self._emit(protocol.EVT_LOG, {"level": level, "message": message})

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Navega a SIIF y autentica. Deja la sesión abierta para `run_batch`."""
        self._log(f"Navegando a {SIIF_URL}")
        self.page.navigate_to(SIIF_URL)

        is_login, message = SIIFLoginProcess(self.page).execute(username, password)
        self._log(message, "info" if is_login else "error")
        return is_login, message

    def run_batch(self) -> dict[str, Any]:
        """Procesa todos los registros del Excel de entrada.

        Returns:
            Resumen con totales de procesados, éxitos, errores y si fue detenido.
        """
        searcher = SearchAccountName(self.driver)
        rows = self.data_manager.load_input().to_dicts()
        total = len(rows)

        self._log(f"Insumo cargado: {total} registros por procesar")
        self._emit(protocol.EVT_RUN_STARTED, {"total": total})

        exitos = 0
        errores = 0
        processed_ids: list = []
        stopped = False

        for position, row in enumerate(rows, start=1):
            if self._stop_event.is_set():
                stopped = True
                self._log("Detención solicitada: se interrumpe el lote", "warning")
                break

            numero_cuenta = str(row.get("NUMERO_CUENTA", ""))
            self._emit(
                protocol.EVT_PROGRESS,
                {"current": position, "total": total, "numero_cuenta": numero_cuenta},
            )

            is_success, message = searcher.execute(**row)
            row["NOMBRE_CUENTA"] = searcher.get_variable("NOMBRE_CUENTA")

            self.data_manager.observe_process(is_success, row, message)
            processed_ids.append(row["INDEX"])

            if is_success:
                exitos += 1
            else:
                errores += 1

            self._emit(
                protocol.EVT_RECORD,
                {
                    "index": row.get("INDEX"),
                    "numero_cuenta": numero_cuenta,
                    "nombre_cuenta": row.get("NOMBRE_CUENTA", ""),
                    "ok": is_success,
                    "message": message,
                },
            )

            if position % BATCH_SIZE == 0:
                self.data_manager.update_entries(processed_ids)
                processed_ids = []
                self._log(f"Lote de {BATCH_SIZE} consolidado en el archivo de entrada")

        self.data_manager.save_observers()
        if processed_ids:
            self.data_manager.update_entries(processed_ids)

        summary = {
            "total": total,
            "procesados": exitos + errores,
            "exitos": exitos,
            "errores": errores,
            "detenido": stopped,
        }
        self._log(
            f"Proceso finalizado. Éxitos: {exitos}, errores: {errores}"
            + (" (detenido por el usuario)" if stopped else "")
        )
        self._emit(protocol.EVT_RUN_FINISHED, summary)
        return summary
