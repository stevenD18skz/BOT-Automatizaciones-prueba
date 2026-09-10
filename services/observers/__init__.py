"""Observadores de la corrida (patrón Observer). El detalle está en base.py."""

from __future__ import annotations

from typing import Callable

from services.observers.base import (
    ProcessObserver,
    RecordResult,
    RunInfo,
    RunNotifier,
    TraceabilityError,
)
from services.observers.events import EventObserver
from services.observers.excel import ExcelResultObserver
from services.observers.trace import TraceObserver


def observadores_por_defecto(
    emit: Callable[[str, dict], None], *, con_excel: bool = True
) -> list[ProcessObserver]:
    """Trazabilidad primero (crítica), Excel después y eventos al final, para que
    el resumen que llega a la UI ya traiga las rutas de los archivos."""
    observers: list[ProcessObserver] = [TraceObserver()]
    if con_excel:
        observers.append(ExcelResultObserver())
    observers.append(EventObserver(emit))
    return observers


__all__ = [
    "EventObserver",
    "ExcelResultObserver",
    "ProcessObserver",
    "RecordResult",
    "RunInfo",
    "RunNotifier",
    "TraceObserver",
    "TraceabilityError",
    "observadores_por_defecto",
]
