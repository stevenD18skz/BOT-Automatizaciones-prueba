"""Módulo PLB / OCD: captura y documentos vía Bot, sin Selenium en Streamlit."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from client.credioro.bot_ops import PrinterService
from client.credioro.bot_ops import (
    BotClientError,
    capture_screen,
    execute_process,
    insolvency_blocks,
    preview_image,
    render_insolvency_banner,
    session_active,
)


def render_validaciones_module() -> None:
    st.markdown('<div class="module-tag">Módulo 2 &bull; Autenticación y Documentos</div>', unsafe_allow_html=True)
    st.markdown("### Validación Biométrica y Autorización en Centrales (PLB / OCD)")
    st.caption("El Bot captura la pantalla SIIF. La UI solo pide refrescar, confirmar o imprimir.")
    render_insolvency_banner()

    solicitud_id = st.session_state.get("solicitud_id", "SOL-CREDIORO")
    st.markdown("#### Validación Biométrica en Vivo (PLB)")
    col_bio1, col_bio2 = st.columns([3, 2])
    with col_bio1:
        img = preview_image(st.session_state.get("plb_preview_path"))
        if img:
            st.image(img, caption="Captura PLB desde el Bot", width='stretch')
        else:
            st.info("Cuando el Bot esté en PLB, use Refrescar para ver el sensor.")
    with col_bio2:
        st.markdown(f"**Estado:** `{st.session_state.get('plb_estado_texto', 'Esperando PLB...')}`")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Refrescar", key="btn_refresh_plb_live", width='stretch'):
                try:
                    response = capture_screen("plb")
                    st.session_state["plb_preview_path"] = (response.data or {}).get("path")
                    st.session_state["plb_estado_texto"] = response.message
                except BotClientError as exc:
                    st.error(str(exc))
                st.rerun()
        with c2:
            if st.button("Confirmar Huella", key="btn_confirm_plb_manual", type="primary", width='stretch'):
                if insolvency_blocks():
                    st.error("Envío bloqueado por insolvencia.")
                elif not session_active():
                    st.info("Inicie sesión SIIF.")
                else:
                    try:
                        response = execute_process(
                            "PLB",
                            solicitud_id=solicitud_id,
                            manual_confirm=True,
                            timeout_segundos=8,
                        )
                    except BotClientError as exc:
                        st.error(str(exc))
                    else:
                        st.session_state["plb_estado_texto"] = response.message
                        if response.ok:
                            st.success(response.message)
                        else:
                            st.error(response.message)

    st.markdown("---")
    st.markdown("#### Autorización en Centrales (OCD - DOC061)")
    col_ocd1, col_ocd2 = st.columns([3, 2])
    with col_ocd1:
        preview = preview_image(st.session_state.get("ocd_preview_path"))
        if preview:
            st.image(preview, caption="Vista previa DOC061", width='stretch')
        else:
            st.info("Use Refrescar Vista o Enviar a Imprimir cuando el Bot esté en OCD.")
    with col_ocd2:
        impresoras = PrinterService.obtener_nombres_impresoras()
        default_idx = 0
        pred = PrinterService.obtener_impresora_predeterminada()
        if pred in impresoras:
            default_idx = impresoras.index(pred)
        impresora_sel = st.selectbox("Seleccionar Impresora:", options=impresoras or ["Predeterminada"], index=default_idx)
        st.session_state["ocd_impresora_seleccionada"] = impresora_sel
        st.markdown(f"**Estado:** `{st.session_state.get('ocd_estado_texto', 'Esperando OCD...')}`")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Enviar a Imprimir", key="btn_imprimir_ocd_manual", type="primary", width='stretch'):
                if insolvency_blocks():
                    st.error("Envío bloqueado por insolvencia.")
                elif not session_active():
                    st.info("Inicie sesión SIIF.")
                else:
                    try:
                        response = execute_process(
                            "OCD",
                            solicitud_id=solicitud_id,
                            impresora=impresora_sel,
                            imprimir=True,
                        )
                    except BotClientError as exc:
                        st.error(str(exc))
                    else:
                        data = response.data or {}
                        st.session_state["ocd_preview_path"] = data.get("preview_path")
                        st.session_state["ocd_pdf_path"] = data.get("pdf_path")
                        st.session_state["ocd_estado_texto"] = response.message
                        if response.ok:
                            st.success(response.message)
                        else:
                            st.error(response.message)
        with b2:
            if st.button("Refrescar Vista", key="btn_refresh_ocd_live", width='stretch'):
                try:
                    response = capture_screen("pdf")
                    data = response.data or {}
                    st.session_state["ocd_preview_path"] = data.get("preview_path") or data.get("path")
                    st.session_state["ocd_pdf_path"] = data.get("path")
                    st.session_state["ocd_estado_texto"] = response.message
                except BotClientError as exc:
                    st.error(str(exc))
                st.rerun()
        pdf_path = st.session_state.get("ocd_pdf_path")
        if pdf_path and Path(pdf_path).exists():
            st.download_button(
                "Descargar PDF Autorización DOC061",
                data=Path(pdf_path).read_bytes(),
                file_name=f"Autorizacion_DOC061_{solicitud_id}.pdf",
                mime="application/pdf",
                width='stretch',
            )
