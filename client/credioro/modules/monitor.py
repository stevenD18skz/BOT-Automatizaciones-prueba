"""Monitor de los 42 mini-procesos. El motor corre en el Bot.

El panel se refresca solo: el Bot empuja un evento por cada proceso que avanza y
el fragmento lo detecta. Solo vuelve a pedir el detalle cuando algo cambió, así
que con el motor parado no genera tráfico.
"""

from __future__ import annotations

import streamlit as st

from client.credioro.catalog import CATALOG_42
from client.credioro.bot_ops import EVT_ENGINE_FINISHED, EVT_ENGINE_PROGRESS
from client.credioro.bot_ops import (
    BotClientError,
    bot_client,
    engine_command,
    insolvency_blocks,
    render_insolvency_banner,
    session_active,
)

STATUS_UI = {
    "PENDING": ("Pendiente", "#94A3B8"),
    "IN_PROGRESS": ("En proceso", "#3B82F6"),
    "COMPLETED": ("Completado", "#22C55E"),
    "ERROR": ("Error", "#EF4444"),
    "SKIPPED": ("Omitido", "#F59E0B"),
    "PAUSED": ("Pausado", "#8B5CF6"),
}

REFRESCO = "0.7s"


def render_proceso_monitor_module() -> None:
    st.markdown('<div class="module-tag">Bot 42P &bull; Monitor de mini-procesos</div>', unsafe_allow_html=True)
    st.markdown("### Motor de 42 mini-procesos")
    st.caption("El Bot ejecuta el catálogo en su propio proceso y empuja su avance a esta pantalla.")
    render_insolvency_banner()

    solicitud_id = st.session_state.get("solicitud_id")
    if not solicitud_id:
        st.info("Primero simule o consulte un cliente para obtener una solicitud.")
        return

    st.session_state.setdefault("monitor_seq", -1)
    st.session_state.setdefault("monitor_data", None)

    @st.fragment(run_every=REFRESCO)
    def panel_motor() -> None:
        _render_panel(solicitud_id)

    panel_motor()


def _leer_estado(solicitud_id: str) -> dict | None:
    """Pide el detalle al Bot solo si llegó algún evento nuevo."""
    client = bot_client()
    seq = client.event_seq
    cacheado = st.session_state.get("monitor_data")

    if cacheado is not None and seq == st.session_state.get("monitor_seq"):
        return cacheado

    try:
        respuesta = engine_command("status", solicitud_id=solicitud_id)
    except BotClientError as exc:
        st.error(str(exc))
        return cacheado

    st.session_state["monitor_seq"] = seq
    st.session_state["monitor_data"] = respuesta.data or {}
    return st.session_state["monitor_data"]


def _render_panel(solicitud_id: str) -> None:
    data = _leer_estado(solicitud_id)
    if data is None:
        return

    runs = data.get("runs") or []
    summary = data.get("summary") or {}
    running = bool(data.get("running"))

    total = summary.get("total") or len(CATALOG_42) or 42
    completed = summary.get("completed") or 0
    st.progress(min(1.0, completed / total if total else 0))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Completados", completed)
    c2.metric("Errores", summary.get("errors") or 0)
    c3.metric("Omitidos", summary.get("skipped") or 0)
    c4.metric("Motor", "En ejecución" if running else "Detenido")

    modo = st.radio(
        "Procesos manuales",
        options=["SKIP", "PAUSE"],
        format_func=lambda x: "Omitir" if x == "SKIP" else "Pausar",
        horizontal=True,
    )
    kwargs_by_code = {
        "OSC": st.session_state.get("sim_payload") or {},
        "OCC": st.session_state.get("occ_payload") or {},
        "OVB": st.session_state.get("ovb_payload") or {},
    }

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Iniciar / Reanudar", type="primary", disabled=running or not session_active(), width='stretch'):
            if insolvency_blocks():
                st.error("El motor no se inicia: el cliente consultado está en insolvencia.")
            else:
                _lanzar("start", solicitud_id, modo, kwargs_by_code)
    with b2:
        if st.button("Reiniciar", disabled=running, width='stretch'):
            if insolvency_blocks():
                st.error("El motor no se reinicia: el cliente consultado está en insolvencia.")
            else:
                _lanzar("restart", solicitud_id, modo, kwargs_by_code)
    with b3:
        if st.button("Detener", disabled=not running, width='stretch'):
            try:
                engine_command("stop")
            except BotClientError as exc:
                st.error(str(exc))
            _invalidar()

    _render_actividad()

    if not runs:
        st.caption("Aún no hay filas de ejecución. Inicie el motor para sembrarlas.")
        return
    rows = []
    for row in runs:
        label, _ = STATUS_UI.get(row.get("status", ""), (row.get("status"), "#64748B"))
        rows.append(
            {
                "Orden": row.get("sort_order"),
                "Código": row.get("process_code"),
                "Grupo": row.get("group_name"),
                "Descripción": row.get("description"),
                "Estado": label,
                "Mensaje": row.get("result_message") or "",
            }
        )
    st.dataframe(rows, width='stretch', hide_index=True)


def _render_actividad() -> None:
    """Últimos avances que el Bot empujó, sin haberlos pedido."""
    eventos = [
        e
        for e in bot_client().recent_events(limit=60)
        if e.event in {EVT_ENGINE_PROGRESS, EVT_ENGINE_FINISHED}
    ]
    if not eventos:
        return
    with st.expander(f"Actividad en vivo del motor ({len(eventos)})", expanded=False):
        lineas = []
        for evento in reversed(eventos[-15:]):
            payload = evento.payload
            if evento.event == EVT_ENGINE_FINISHED:
                lineas.append(f"FIN — {payload.get('completed', 0)} completados, {payload.get('errors', 0)} errores")
            else:
                lineas.append(
                    f"{payload.get('code', '')} → {payload.get('status', '')} {payload.get('message', '')}".strip()
                )
        st.code("\n".join(lineas), language=None)


def _lanzar(action: str, solicitud_id: str, modo: str, kwargs_by_code: dict) -> None:
    try:
        response = engine_command(
            action,
            solicitud_id=solicitud_id,
            manual_mode=modo,
            kwargs_by_code=kwargs_by_code,
        )
        st.info(response.message)
    except BotClientError as exc:
        st.error(str(exc))
    _invalidar()


def _invalidar() -> None:
    """Fuerza que el próximo refresco vuelva a pedir el detalle al Bot."""
    st.session_state["monitor_seq"] = -1
