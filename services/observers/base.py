"""Patrón Observer de la corrida de un proceso.

El orquestador es el sujeto: por cada registro avisa "empieza" y "terminó con tal
resultado", y al final "cerré la corrida". Los observadores deciden qué hacer con
cada aviso (escribir la trazabilidad, generar los Excel, empujar eventos a la UI)
sin que el orquestador conozca a ninguno en concreto.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

logger = logging.getLogger(__name__)


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


class TraceabilityError(RuntimeError):
    """Un observador crítico no pudo registrar: no se procesa nada sin dejar rastro."""


@dataclass
class RunInfo:
    run_id: str
    modo: str  # "real" si toca SIIF, "demo" si es simulado
    usuario: str
    inicio: str
    total: int = 0
    origen: str = "lote"  # de dónde salen los datos: "lote" (ENTRADAS.xlsx) o "ui"


@dataclass
class RecordResult:
    run_id: str
    posicion: int
    total: int
    entrada: dict[str, Any]
    salida: dict[str, Any]
    ok: bool
    mensaje: str
    inicio: str
    fin: str
    duracion_ms: int


class ProcessObserver:
    """Avisos vacíos por defecto: cada observador sobrescribe los que necesita.

    `critical = True`: si el observador falla, la corrida se detiene en lugar de
    seguir procesando registros sin dejar constancia.
    """

    critical = False

    def on_run_started(self, run: RunInfo) -> None:
        pass

    def on_record_started(self, run: RunInfo, posicion: int, entrada: dict[str, Any]) -> None:
        pass

    def on_record(self, result: RecordResult) -> None:
        pass

    def on_run_finished(self, run: RunInfo, summary: dict[str, Any]) -> None:
        pass


class RunNotifier:
    """El sujeto del patrón: lleva la cuenta de la corrida y avisa a los observadores.

    Los avisos llegan en el orden de la lista, y en el cierre cada observador puede
    añadir datos al resumen (la ruta de su archivo, por ejemplo). Por eso los que
    solo reenvían, como los eventos a la UI, van al final.
    """

    def __init__(
        self,
        observers: Iterable[ProcessObserver],
        *,
        modo: str = "real",
        usuario: str = "",
        origen: str = "lote",
    ) -> None:
        self.observers = list(observers)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.run = RunInfo(
            run_id=f"{stamp}-{uuid.uuid4().hex[:4]}",
            modo=modo,
            usuario=usuario or "",
            inicio=ahora(),
            origen=origen,
        )
        self.exitos = 0
        self.errores = 0
        self.summary: dict[str, Any] | None = None
        self._t0 = time.perf_counter()
        self._started = False
        self._rec_inicio = ""
        self._rec_t0 = 0.0

    def _notify(self, method: str, *args: Any, strict: bool = True) -> None:
        for observer in self.observers:
            try:
                getattr(observer, method)(*args)
            except Exception as exc:
                nombre = type(observer).__name__
                logger.exception("El observador %s falló en %s", nombre, method)
                if observer.critical and strict:
                    raise TraceabilityError(
                        f"{nombre} no pudo registrar la trazabilidad: {exc}"
                    ) from exc

    def start(self, total: int, *, strict: bool = True) -> None:
        self.run.total = total
        self._started = True
        self._notify("on_run_started", self.run, strict=strict)

    def begin_record(self, posicion: int, entrada: dict[str, Any]) -> None:
        self._rec_inicio = ahora()
        self._rec_t0 = time.perf_counter()
        self._notify("on_record_started", self.run, posicion, entrada)

    def record(
        self,
        posicion: int,
        entrada: dict[str, Any],
        ok: bool,
        mensaje: str,
        salida: dict[str, Any] | None = None,
    ) -> RecordResult:
        result = RecordResult(
            run_id=self.run.run_id,
            posicion=posicion,
            total=self.run.total,
            entrada=dict(entrada),
            salida=dict(salida or {}),
            ok=bool(ok),
            mensaje=str(mensaje),
            inicio=self._rec_inicio or ahora(),
            fin=ahora(),
            duracion_ms=int((time.perf_counter() - self._rec_t0) * 1000),
        )
        self._notify("on_record", result)
        # Se cuenta después de avisar: si la trazabilidad falló, no cuenta como procesado.
        if result.ok:
            self.exitos += 1
        else:
            self.errores += 1
        return result

    def finish(self, *, detenido: bool = False, error: str | None = None) -> dict[str, Any]:
        """Cierra la corrida. No lanza nunca: se llama desde un `finally`."""
        if self.summary is not None:
            return self.summary
        if not self._started:
            self.start(self.run.total, strict=False)
        self.summary = {
            "run_id": self.run.run_id,
            "modo": self.run.modo,
            "origen": self.run.origen,
            "usuario": self.run.usuario,
            "total": self.run.total,
            "procesados": self.exitos + self.errores,
            "exitos": self.exitos,
            "errores": self.errores,
            "detenido": detenido,
            "error": error,
            "duracion_s": round(time.perf_counter() - self._t0, 1),
        }
        self._notify("on_run_finished", self.run, self.summary, strict=False)
        return self.summary
