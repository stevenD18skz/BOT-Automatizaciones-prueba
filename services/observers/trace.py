"""Trazabilidad de la corrida: una línea JSON por evento, en disco al instante.

Se usa JSON Lines y no Excel a propósito: un .xlsx no admite añadir filas, hay que
reescribirlo entero, y si alguien lo tiene abierto en Excel ni eso. Aquí cada
registro se escribe y se sincroniza con el disco antes de pasar al siguiente, así
que ni matar el proceso ni un corte de luz pierden lo ya procesado.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

import config.settings as settings
from services.observers.base import ProcessObserver, RecordResult, RunInfo, ahora


class TraceObserver(ProcessObserver):
    critical = True

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = Path(directory) if directory else settings.TRACE_DIR
        self.path: Path | None = None

    def _append(self, data: dict[str, Any]) -> None:
        assert self.path is not None
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(data, ensure_ascii=False, default=str) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def on_run_started(self, run: RunInfo) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        # El nombre dice de un vistazo qué fue: 20260910-...-demo-ui.jsonl
        partes = [run.run_id]
        if run.modo != "real":
            partes.append(run.modo)
        if run.origen != "lote":
            partes.append(run.origen)
        self.path = self.directory / f"{'-'.join(partes)}.jsonl"
        self._append(
            {
                "tipo": "inicio",
                "run_id": run.run_id,
                "modo": run.modo,
                "origen": run.origen,
                "usuario": run.usuario,
                "fecha": run.inicio,
                "total": run.total,
                "bot": settings.BOT_NAME,
                "proceso": settings.PROCESS_NAME,
            }
        )

    def on_record(self, result: RecordResult) -> None:
        self._append({"tipo": "registro", **asdict(result)})

    def on_run_finished(self, run: RunInfo, summary: dict[str, Any]) -> None:
        if self.path is None:
            return
        summary["trazabilidad"] = str(self.path)
        self._append({"tipo": "fin", "fecha": ahora(), **summary})
