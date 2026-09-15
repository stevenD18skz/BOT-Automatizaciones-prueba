"""Módulo ORC: decisión del estudio capturada por el Bot."""

from __future__ import annotations

import streamlit as st

from client.credioro.bot_ops import (
    BotClientError,
    execute_process,
    insolvency_blocks,
    render_insolvency_banner,
    session_active,
)
from client.credioro.modules.simulador import _fmt_cop, _kpi_html


def _decision_html(decision: str) -> str:
    texto = str(decision).strip().upper()
    aprobado = "APROBADO" in texto
    rechazado = texto not in ("—", "", "NONE") and not aprobado
    if aprobado:
        titulo, badge, cls = "CRÉDITO APROBADO", "Aprobado por SIIF", "decision-card-aprobado"
    elif rechazado:
        titulo, badge, cls = "CRÉDITO RECHAZADO", "Rechazado por SIIF", "decision-card-rechazado"
    else:
        titulo, badge, cls = "PENDIENTE DE ESTUDIO", "Pendiente de Captura", "decision-card-pendiente"
    return (
        f'<div class="decision-card {cls}"><div class="decision-content">'
        f'<span class="decision-title-tag">Resultado Oficial · SIIF</span> '
        f'<span class="decision-badge">{badge}</span>'
        f'<div class="decision-main-text">{titulo}</div></div></div>'
    )


def render_orc_module() -> None:
    st.markdown('<div class="module-tag">Módulo ORC &bull; Resultado del Estudio</div>', unsafe_allow_html=True)
    st.markdown("### Resultado del Estudio de Crédito (ORC)")
    st.caption("El Bot lee la decisión en SIIF. Los campos de este módulo no se deshabilitan.")
    render_insolvency_banner()
    st.session_state.setdefault("orc_decision", "—")
    st.session_state.setdefault("orc_valor_credito", "—")

    st.markdown(_decision_html(st.session_state["orc_decision"]), unsafe_allow_html=True)
    valor = st.session_state.get("orc_valor_credito", "—")
    valor_fmt = _fmt_cop(str(valor)) if str(valor) not in ("—", "", "None") else "—"
    st.markdown(f'<div class="sim-grid">{_kpi_html("Valor del Crédito", valor_fmt, highlight=True)}</div>', unsafe_allow_html=True)

    _, col_centro, _ = st.columns([1.2, 1, 1.2])
    with col_centro:
        enviar = st.button("Enviar", key="btn_orc_enviar", width='stretch', type="primary")
    if not enviar:
        return
    if insolvency_blocks():
        st.error("Envío bloqueado por insolvencia.")
        return
    if not session_active():
        st.info("Inicie sesión SIIF.")
        return
    try:
        response = execute_process("ORC")
    except BotClientError as exc:
        st.error(str(exc))
        return
    data = response.data or {}
    if data.get("decision"):
        st.session_state["orc_decision"] = data["decision"]
    if data.get("valor_credito"):
        st.session_state["orc_valor_credito"] = data["valor_credito"]
    st.session_state["orc_completado"] = response.ok
    if response.ok:
        st.success(response.message)
        st.rerun()
    else:
        st.error(response.message)
