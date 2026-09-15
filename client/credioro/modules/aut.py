"""Módulo AUT: solicitud y confirmación de OTP vía Bot."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from client.credioro.bot_ops import (
    BotClientError,
    execute_process,
    insolvency_blocks,
    render_insolvency_banner,
    session_active,
)


def render_aut_module() -> None:
    st.markdown('<div class="module-tag">AUT &bull; Autorización & Código OTP</div>', unsafe_allow_html=True)
    st.markdown("### Autorización del Cliente (AUT)")
    st.caption("Paso posterior a OVB: el Bot solicita y confirma el código OTP en SIIF.")
    render_insolvency_banner()

    defaults = {
        "aut_codigo_otp": "",
        "aut_solicitado": False,
        "aut_completado": False,
        "aut_mensaje_estado": "Esperando solicitud de código OTP.",
        "aut_timestamp_solicitud": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    with st.container(border=True):
        st.markdown(
            f"**Gestión de OTP** — Solicitud: `{st.session_state.get('solicitud_id') or 'N/A'}`"
        )
        _, col_btn, _ = st.columns(3)
        with col_btn:
            if st.button("Solicitar Código OTP", width='stretch', key="btn_aut_solicitar"):
                if insolvency_blocks():
                    st.error("Envío bloqueado por insolvencia.")
                elif not session_active():
                    st.info("Inicie sesión SIIF.")
                else:
                    try:
                        response = execute_process("AUT", accion="solicitar")
                    except BotClientError as exc:
                        st.error(str(exc))
                    else:
                        if response.ok:
                            st.session_state["aut_solicitado"] = True
                            st.session_state["aut_timestamp_solicitud"] = datetime.now().strftime("%H:%M:%S")
                            st.session_state["aut_mensaje_estado"] = response.message
                            st.success(response.message)
                        else:
                            st.error(response.message)

        with st.form("form_aut_codigo"):
            codigo_input = st.text_input("Código OTP", value=st.session_state["aut_codigo_otp"], max_chars=20)
            continuar = st.form_submit_button("Continuar", width='stretch', type="primary")
        if continuar:
            if insolvency_blocks():
                st.error("Envío bloqueado por insolvencia.")
            elif not codigo_input.strip():
                st.error("Debe ingresar el código OTP.")
            elif not session_active():
                st.info("Inicie sesión SIIF.")
            else:
                try:
                    response = execute_process("AUT", accion="confirmar", codigo_otp=codigo_input.strip())
                except BotClientError as exc:
                    st.error(str(exc))
                else:
                    st.session_state["aut_codigo_otp"] = codigo_input.strip()
                    if response.ok:
                        st.session_state["aut_completado"] = True
                        st.success(response.message)
                    else:
                        st.error(response.message)

    if st.session_state.get("aut_completado"):
        st.markdown(
            f"<div class='result-card'><h4>Autorización OTP confirmada</h4>"
            f"<p>Código: <code>{st.session_state.get('aut_codigo_otp')}</code></p></div>",
            unsafe_allow_html=True,
        )
