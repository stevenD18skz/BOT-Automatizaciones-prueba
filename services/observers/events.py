"""Reenvía los avisos de la corrida a la UI como eventos del protocolo."""

from __future__ import annotations

from typing import Any, Callable

import protocol
from services.observers.base import ProcessObserver, RecordResult, RunInfo


class EventObserver(ProcessObserver):
    def __init__(
        self, emit: Callable[[str, dict], None], campo_etiqueta: str = "NUMERO_CUENTA"
    ) -> None:
        self._emit = emit
        self._campo = campo_etiqueta

    def on_run_started(self, run: RunInfo) -> None:
        self._emit(
            protocol.EVT_RUN_STARTED,
            {"total": run.total, "run_id": run.run_id, "modo": run.modo, "origen": run.origen},
        )

    def on_record_started(self, run: RunInfo, posicion: int, entrada: dict[str, Any]) -> None:
        self._emit(
            protocol.EVT_PROGRESS,
            {
                "current": posicion,
                "total": run.total,
                "numero_cuenta": str(entrada.get(self._campo, "")),
            },
        )

    def on_record(self, result: RecordResult) -> None:
        self._emit(
            protocol.EVT_RECORD,
            {
                "index": result.entrada.get("INDEX"),
                "numero_cuenta": str(result.entrada.get(self._campo, "")),
                "nombre_cuenta": str(result.salida.get("NOMBRE_CUENTA") or ""),
                "ok": result.ok,
                "message": result.mensaje,
                "duracion_ms": result.duracion_ms,
                "run_id": result.run_id,
            },
        )

    def on_run_finished(self, run: RunInfo, summary: dict[str, Any]) -> None:
        self._emit(protocol.EVT_RUN_FINISHED, dict(summary))
