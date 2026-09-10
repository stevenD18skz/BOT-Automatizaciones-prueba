"""Consulta de cuentas escritas en la UI, con el proceso de la plantilla."""

import json
import time
from pathlib import Path

import config.settings as settings
import protocol
import services.workflows.orchestrator as orch_mod
from bot.session import BotSession
from core.process import BaseProcess
from services.data.cuentas import MAX_CUENTAS_POR_CONSULTA, limpiar_cuentas, separar
from services.data.data_manager import DataManager
from services.workflows.orchestrator import Orchestrator


class _Driver:
    """BasePage solo guarda la referencia; ningún test abre un navegador."""


class _Buscador(BaseProcess):
    """Encuentra todas las cuentas salvo las que terminan en 0."""

    def execute(self, **data):
        cuenta = data["NUMERO_CUENTA"]
        if cuenta.endswith("0"):
            return False, "Cuenta no encontrada"
        self.set_variable("NOMBRE_CUENTA", f"TITULAR {cuenta}")
        return True, "Proceso ejecutado exitosamente"


def _esperar(sesion: BotSession) -> None:
    for _ in range(200):
        if not sesion.running:
            return
        time.sleep(0.05)
    raise AssertionError("la corrida no terminó")


def _lineas(archivo: Path) -> list[dict]:
    return [json.loads(linea) for linea in archivo.read_text(encoding="utf-8").splitlines()]


# --- validación de lo que se escribe ---------------------------------------
def test_limpiar_cuentas_valida_y_quita_duplicados():
    validas, invalidas = limpiar_cuentas(["001-234", " 001234 ", "12a4", "", "555"])
    assert validas == ["001234", "555"]
    assert invalidas == ["12a4"]


def test_separar_acepta_lineas_comas_y_espacios():
    assert separar("111\n222, 333 ;444") == ["111", "222", "333", "444"]


def test_un_texto_se_separa_en_vez_de_iterar_caracteres():
    assert limpiar_cuentas("111\n222")[0] == ["111", "222"]


# --- consulta real (con el proceso simulado) --------------------------------
def test_consulta_desde_la_ui_queda_trazada_y_no_toca_entradas_ni_excel(rutas, monkeypatch):
    tmp, _ = rutas
    monkeypatch.setattr(orch_mod, "SearchAccountName", _Buscador)
    orch = Orchestrator(_Driver())
    orch.username = "cajero01"
    orch.data_manager = DataManager(tmp / "no_existe.xlsx")  # la consulta no debe leerlo

    summary = orch.run_consulta(["111", "220"])

    assert summary["origen"] == "ui"
    assert (summary["exitos"], summary["errores"]) == (1, 1)
    archivo = Path(summary["trazabilidad"])
    assert archivo.name.endswith("-ui.jsonl")
    lineas = _lineas(archivo)
    assert lineas[0]["usuario"] == "cajero01"
    assert lineas[0]["origen"] == "ui"
    registros = [linea for linea in lineas if linea["tipo"] == "registro"]
    assert [r["entrada"]["NUMERO_CUENTA"] for r in registros] == ["111", "220"]
    assert registros[0]["salida"]["NOMBRE_CUENTA"] == "TITULAR 111"
    assert not settings.OUTPUT_FILE_PATH.exists()
    assert not settings.ERROR_FILE_PATH.exists()


def test_consultar_exige_sesion_y_cuentas_validas():
    sesion = BotSession(emit=lambda _e, _p: None)
    ok, mensaje = sesion.consultar(["111"])
    assert not ok and "sesión" in mensaje

    sesion.logged_in = True
    sesion._orchestrator = object()  # la validación corta antes de usarlo
    ok, mensaje = sesion.consultar(["12a"])
    assert not ok and "12a" in mensaje
    ok, mensaje = sesion.consultar([])
    assert not ok and "al menos" in mensaje
    ok, mensaje = sesion.consultar([str(i) for i in range(MAX_CUENTAS_POR_CONSULTA + 1)])
    assert not ok and "Máximo" in mensaje
    assert not sesion.running


def test_consultar_corre_en_segundo_plano_y_la_ui_recibe_los_nombres(rutas, monkeypatch):
    monkeypatch.setattr(orch_mod, "SearchAccountName", _Buscador)
    eventos: list[tuple[str, dict]] = []
    sesion = BotSession(emit=lambda e, p: eventos.append((e, p)))
    sesion.logged_in = True
    sesion._orchestrator = Orchestrator(
        _Driver(), on_event=sesion._track, stop_event=sesion._stop_event
    )

    ok, mensaje = sesion.consultar("111\n333")
    assert ok and "2 cuenta" in mensaje
    _esperar(sesion)

    assert sesion.last_summary["origen"] == "ui"
    assert sesion.last_summary["exitos"] == 2
    registros = [p for e, p in eventos if e == protocol.EVT_RECORD]
    assert [r["nombre_cuenta"] for r in registros] == ["TITULAR 111", "TITULAR 333"]


def test_la_demo_simula_las_cuentas_escritas_en_la_ui(rutas):
    tmp, _ = rutas
    sesion = BotSession(emit=lambda _e, _p: None)

    ok, _ = sesion.demo(pausa=0, cuentas=["777", "888"])
    assert ok
    _esperar(sesion)

    archivo = next((tmp / "trazabilidad").glob("*-demo-ui.jsonl"))
    registros = [linea for linea in _lineas(archivo) if linea["tipo"] == "registro"]
    assert [r["entrada"]["NUMERO_CUENTA"] for r in registros] == ["777", "888"]
