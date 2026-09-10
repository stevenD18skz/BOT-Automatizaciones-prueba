"""Excel de negocio de la corrida: CONCILIACION (éxitos) y ERRORES (fallos).

Conservan las columnas de siempre. Se escriben al cerrar la corrida, que el
orquestador hace en un `finally`: detenida, completa o con error, siempre quedan.
El detalle registro a registro, a prueba de caídas, es la trazabilidad.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import polars as pl

import config.settings as settings
from services.observers.base import ProcessObserver, RecordResult, RunInfo

logger = logging.getLogger(__name__)

COLUMNAS = ("INDEX", "FECHA", "NUMERO_CUENTA", "NOMBRE_CUENTA", "MESSAGE")


class ExcelResultObserver(ProcessObserver):
    def __init__(self, output_path: Path | None = None, error_path: Path | None = None) -> None:
        self.output_path = Path(output_path) if output_path else settings.OUTPUT_FILE_PATH
        self.error_path = Path(error_path) if error_path else settings.ERROR_FILE_PATH
        self._exitos: list[dict[str, str]] = []
        self._errores: list[dict[str, str]] = []

    def on_run_started(self, run: RunInfo) -> None:
        self._exitos, self._errores = [], []

    def on_record(self, result: RecordResult) -> None:
        fila = {
            "INDEX": str(result.entrada.get("INDEX", "")),
            "FECHA": result.fin.replace("T", " "),
            "NUMERO_CUENTA": str(result.entrada.get("NUMERO_CUENTA", "")),
            "NOMBRE_CUENTA": str(result.salida.get("NOMBRE_CUENTA") or ""),
            "MESSAGE": result.mensaje,
        }
        (self._exitos if result.ok else self._errores).append(fila)

    def on_run_finished(self, run: RunInfo, summary: dict[str, Any]) -> None:
        # Se escriben los dos siempre, aunque estén vacíos: un ERRORES.xlsx de una
        # corrida anterior no debe hacerse pasar por el de esta.
        summary["conciliacion"] = str(_guardar(self._exitos, self.output_path, run.run_id))
        summary["errores_xlsx"] = str(_guardar(self._errores, self.error_path, run.run_id))


def _guardar(filas: list[dict[str, str]], destino: Path, run_id: str) -> Path:
    df = pl.DataFrame(filas, schema={col: pl.String for col in COLUMNAS})
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.write_excel(destino)
        return destino
    except Exception as exc:
        # Lo típico: el archivo está abierto en Excel. Se guarda con otro nombre en
        # vez de perder el resultado de la corrida.
        alterno = destino.with_name(f"{destino.stem}_{run_id}{destino.suffix}")
        logger.warning(
            "No se pudo escribir %s (%s); se guarda en %s", destino.name, exc, alterno.name
        )
        df.write_excel(alterno)
        return alterno
