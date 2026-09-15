"""Maqueta de los helpers de UI de credioro-app.

Los módulos de CrediOro (simulador, cliente, OIF, ORC, ...) se trajeron tal cual
desde credioro-app, pero aquí NO están conectados a ningún Bot: todo lo que en el
original viajaba al proceso Selenium termina en `BotClientError`, que los módulos
ya muestran como un `st.error`. Así la interfaz se ve y se navega completa sin
ejecutar nada.

Lo único funcional de esta UI es la Consulta de Cuentas de Ahorros, que usa el
cliente real de `client/ipc.py`.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any

import streamlit as st

MENSAJE_MAQUETA = (
    "Maqueta visual: este módulo de CrediOro todavía no está conectado al Bot. "
    "Por ahora solo funciona la Consulta de Cuentas de Ahorros."
)

# Constantes que los módulos importaban del protocolo de credioro-app
STATUS_BLOCKED = "blocked"
EVT_ENGINE_PROGRESS = "engine_progress"
EVT_ENGINE_FINISHED = "engine_finished"


class BotClientError(Exception):
    """En la maqueta, cualquier llamada al Bot termina aquí."""


class _ClienteMaqueta:
    """Imita la forma del BotClient de credioro sin abrir ninguna conexión."""

    host = "—"
    port = "—"
    event_seq = 0

    def start(self) -> None:
        pass

    def recent_events(self, limit: int = 40) -> list:
        return []

    def __getattr__(self, name: str):
        # simulate(), execute(), capture(), engine()... todas fallan igual
        def _sin_conexion(*_args, **_kwargs):
            raise BotClientError(MENSAJE_MAQUETA)

        return _sin_conexion


BotClient = _ClienteMaqueta  # el simulador lo instancia directamente
_CLIENTE = _ClienteMaqueta()


def bot_client() -> _ClienteMaqueta:
    return _CLIENTE


def ensure_bot_running(client: _ClienteMaqueta | None = None) -> _ClienteMaqueta:
    return client or _CLIENTE


def session_active() -> bool:
    return bool(st.session_state.get("siif_session_active"))


def insolvency_blocks() -> bool:
    return bool(st.session_state.get("cliente_bloqueado_insolvencia"))


def render_insolvency_banner() -> None:
    if not insolvency_blocks():
        return
    name = (
        st.session_state.get("cliente_nombre_insolvencia")
        or st.session_state.get("sim_nombre_cliente")
        or "Cliente"
    )
    doc = st.session_state.get("sim_num_doc_val") or st.session_state.get("cliente_num_doc") or ""
    st.error(
        f"BLOQUEO POR INSOLVENCIA (Ley 1564): **{name}** (Doc: `{doc}`). "
        "Los formularios siguen editables. Si consulta otro documento habilitado, "
        "el bloqueo se levanta solo. El envío a SIIF permanece restringido para este cliente."
    )


def execute_process(code: str, **payload: Any):
    raise BotClientError(MENSAJE_MAQUETA)


def capture_screen(kind: str = "screenshot"):
    raise BotClientError(MENSAJE_MAQUETA)


def engine_command(action: str, **payload: Any):
    raise BotClientError(MENSAJE_MAQUETA)


def preview_image(path: str | None):
    if path and Path(path).exists():
        return str(path)
    return None


class InsolvencyService:
    """Sin base de insolvencia en este proyecto: nunca bloquea."""

    @staticmethod
    def clean_document(num_doc: str) -> str:
        return re.sub(r"\D", "", num_doc or "")

    @staticmethod
    def lookup_by_document(num_doc: str) -> dict:
        return {
            "base_disponible": False,
            "mensaje": "Maqueta: la base de insolvencia no está conectada en este proyecto.",
        }


class PrinterService:
    """Sin impresoras reales: la maqueta solo muestra el selector."""

    @staticmethod
    def obtener_nombres_impresoras() -> list[str]:
        return []

    @staticmethod
    def obtener_impresora_predeterminada() -> str:
        return ""


class settings:  # noqa: N801 - imita el módulo `settings` de credioro-app
    @staticmethod
    def dataset_dir(nombre: str) -> Path:
        return Path(tempfile.gettempdir()) / "credioro_maqueta" / nombre
