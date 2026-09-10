"""Trazabilidad de la corrida: cada resultado debe quedar guardado pase lo que pase."""

import json
import subprocess
import sys
import threading
import time
from pathlib import Path

import polars as pl
import pytest

import config.settings as settings
import services.workflows.orchestrator as orch_mod
from core.process import BaseProcess
from services.data.data_manager import DataManager
from services.observers import TraceabilityError, TraceObserver
from services.workflows.orchestrator import Orchestrator

ROOT = Path(__file__).resolve().parent.parent


class _Driver:
    """BasePage solo guarda la referencia; ningún test abre un navegador."""


def _crear_entrada(path: Path, n: int) -> None:
    pl.DataFrame(
        {
            "INDEX": [str(i) for i in range(1, n + 1)],
            "NUMERO_CUENTA": [f"000{i:05d}" for i in range(1, n + 1)],
        }
    ).write_excel(path)


def _leer_traza(tmp_path: Path) -> list[dict]:
    archivos = list((tmp_path / "trazabilidad").glob("*.jsonl"))
    assert len(archivos) == 1, archivos
    return [json.loads(linea) for linea in archivos[0].read_text(encoding="utf-8").splitlines()]


def _orquestador(entrada, proceso_cls, monkeypatch, stop_event=None) -> Orchestrator:
    monkeypatch.setattr(orch_mod, "SearchAccountName", proceso_cls)
    orch = Orchestrator(_Driver(), stop_event=stop_event)
    orch.data_manager = DataManager(entrada)
    orch.username = "cajero01"
    return orch


class _Alterna(BaseProcess):
    """Éxito en los impares (con nombre) y fallo en los pares (sin tocar el nombre)."""

    def execute(self, **data):
        i = int(data["INDEX"])
        if i % 2:
            self.set_variable("NOMBRE_CUENTA", f"CLIENTE {i}")
            return True, "ok"
        return False, "Cuenta no encontrada"


def test_la_corrida_completa_queda_trazada(rutas, monkeypatch):
    tmp, entrada = rutas
    _crear_entrada(entrada, 3)

    summary = _orquestador(entrada, _Alterna, monkeypatch).run_batch()

    lineas = _leer_traza(tmp)
    assert [linea["tipo"] for linea in lineas] == ["inicio", "registro", "registro", "registro", "fin"]
    assert lineas[0]["usuario"] == "cajero01"
    assert all(linea["duracion_ms"] >= 0 for linea in lineas if linea["tipo"] == "registro")
    assert (summary["exitos"], summary["errores"]) == (2, 1)
    assert Path(summary["trazabilidad"]).exists()
    assert pl.read_excel(entrada).height == 0  # todos retirados de la entrada


def test_un_fallo_no_hereda_el_nombre_del_cliente_anterior(rutas, monkeypatch):
    tmp, entrada = rutas
    _crear_entrada(entrada, 4)

    _orquestador(entrada, _Alterna, monkeypatch).run_batch()

    registros = [linea for linea in _leer_traza(tmp) if linea["tipo"] == "registro"]
    assert registros[1]["ok"] is False
    assert "NOMBRE_CUENTA" not in registros[1]["salida"]  # antes traía "CLIENTE 1"
    errores = pl.read_excel(settings.ERROR_FILE_PATH, infer_schema_length=0)
    assert errores["NOMBRE_CUENTA"].fill_null("").to_list() == ["", ""]


class _RevientaEnElTercero(BaseProcess):
    def execute(self, **data):
        if data["INDEX"] == "3":
            raise RuntimeError("se cayó el navegador")
        return True, "ok"


def test_si_revienta_a_mitad_nada_sale_de_la_entrada_sin_quedar_trazado(rutas, monkeypatch):
    tmp, entrada = rutas
    monkeypatch.setattr(orch_mod, "BATCH_SIZE", 2)
    _crear_entrada(entrada, 5)

    with pytest.raises(RuntimeError):
        _orquestador(entrada, _RevientaEnElTercero, monkeypatch).run_batch()

    lineas = _leer_traza(tmp)
    assert lineas[-1]["tipo"] == "fin"
    assert "se cayó el navegador" in lineas[-1]["error"]
    trazados = {linea["entrada"]["INDEX"] for linea in lineas if linea["tipo"] == "registro"}
    quedan = set(pl.read_excel(entrada, infer_schema_length=0)["INDEX"].to_list())
    retirados = {"1", "2", "3", "4", "5"} - quedan
    assert retirados <= trazados
    assert quedan == {"3", "4", "5"}  # el que falló sigue en la entrada para reintentarse


def test_detener_cierra_la_corrida_con_todo_guardado(rutas, monkeypatch):
    tmp, entrada = rutas
    _crear_entrada(entrada, 5)
    stop = threading.Event()

    class _ParaEnElSegundo(BaseProcess):
        def execute(self, **data):
            if data["INDEX"] == "2":
                stop.set()
            self.set_variable("NOMBRE_CUENTA", "X")
            return True, "ok"

    summary = _orquestador(entrada, _ParaEnElSegundo, monkeypatch, stop_event=stop).run_batch()

    assert summary["detenido"] is True
    assert summary["procesados"] == 2
    assert pl.read_excel(settings.OUTPUT_FILE_PATH).height == 2
    assert _leer_traza(tmp)[-1]["detenido"] is True


def test_si_conciliacion_esta_bloqueado_se_guarda_con_otro_nombre(rutas, monkeypatch):
    _, entrada = rutas
    _crear_entrada(entrada, 1)
    destino = settings.OUTPUT_FILE_PATH
    destino.parent.mkdir(parents=True)
    destino.write_bytes(b"")
    destino.chmod(0o444)  # solo lectura, como cuando alguien lo tiene abierto en Excel
    try:
        summary = _orquestador(entrada, _Alterna, monkeypatch).run_batch()
    finally:
        destino.chmod(0o666)

    alterno = Path(summary["conciliacion"])
    assert alterno != destino
    assert alterno.name.startswith("CONCILIACION_")
    assert alterno.exists()


def test_si_no_se_puede_escribir_la_traza_la_corrida_se_detiene(rutas, monkeypatch):
    _, entrada = rutas
    _crear_entrada(entrada, 3)
    ejecutados: list[str] = []

    class _Cuenta(BaseProcess):
        def execute(self, **data):
            ejecutados.append(data["INDEX"])
            return True, "ok"

    def _disco_lleno(self, result):
        raise OSError("disco lleno")

    monkeypatch.setattr(TraceObserver, "on_record", _disco_lleno)

    with pytest.raises(TraceabilityError):
        _orquestador(entrada, _Cuenta, monkeypatch).run_batch()

    assert ejecutados == ["1"]  # no siguió procesando sin dejar rastro
    assert pl.read_excel(entrada).height == 3  # ni retiró nada de la entrada


def test_matar_el_proceso_no_pierde_lo_ya_procesado(tmp_path):
    """Sin finally ni cierre ordenado: os._exit a mitad de la corrida, como un kill."""
    codigo = f"""
import os, sys
sys.path.insert(0, {str(ROOT)!r})
from pathlib import Path
from services.observers import RunNotifier, TraceObserver
n = RunNotifier([TraceObserver(Path({str(tmp_path)!r}))], usuario="cajero01")
n.start(5)
for i in range(1, 6):
    n.begin_record(i, {{"INDEX": str(i)}})
    if i == 4:
        os._exit(1)
    n.record(i, {{"INDEX": str(i)}}, True, "ok")
"""
    subprocess.run([sys.executable, "-c", codigo], cwd=ROOT, check=False, timeout=60)

    archivo = next(tmp_path.glob("*.jsonl"))
    lineas = [json.loads(linea) for linea in archivo.read_text(encoding="utf-8").splitlines()]
    assert [linea["tipo"] for linea in lineas] == ["inicio", "registro", "registro", "registro"]


def test_la_demo_deja_trazabilidad_marcada_y_no_toca_los_excel(rutas):
    tmp, _ = rutas
    from bot.session import BotSession

    sesion = BotSession(emit=lambda _evento, _payload: None)
    sesion.demo(registros=4, pausa=0)
    for _ in range(200):
        if not sesion.running:
            break
        time.sleep(0.05)

    archivo = next((tmp / "trazabilidad").glob("*-demo.jsonl"))
    lineas = [json.loads(linea) for linea in archivo.read_text(encoding="utf-8").splitlines()]
    assert lineas[0]["modo"] == "demo"
    assert lineas[-1]["tipo"] == "fin"
    assert sum(linea["tipo"] == "registro" for linea in lineas) == 4
    assert not settings.OUTPUT_FILE_PATH.exists()
    assert sesion.last_summary["trazabilidad"] == str(archivo)
