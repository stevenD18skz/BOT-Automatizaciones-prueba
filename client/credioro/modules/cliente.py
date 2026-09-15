"""Módulo OCC: consulta y datos del cliente. Formularios siempre editables."""

from __future__ import annotations

import streamlit as st

from client.credioro.bot_ops import (
    BotClientError,
    execute_process,
    insolvency_blocks,
    render_insolvency_banner,
    session_active,
)


def render_cliente_module() -> None:
    st.markdown('<div class="module-tag">Módulo 1 &bull; Consulta Cliente (OCC)</div>', unsafe_allow_html=True)
    st.markdown("### Consulta y Datos del Cliente")
    st.caption("Verificación y edición de información personal, país de origen y modalidad de CrediOro en SIIF.")
    render_insolvency_banner()

    defaults = {
        "cliente_primer_nombre": "",
        "cliente_otros_nombres": "",
        "cliente_primer_apellido": "",
        "cliente_segundo_apellido": "",
        "cliente_pais_origen": "CO",
        "cliente_cred_tradicional": "SI",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    with st.form("form_cliente_credioro", clear_on_submit=False):
        c_n1, c_n2 = st.columns(2)
        with c_n1:
            primer_nombre = st.text_input("Primer Nombre", value=st.session_state["cliente_primer_nombre"], key="occ_primer_nom")
        with c_n2:
            otros_nombres = st.text_input("Segundo Nombre / Otros Nombres", value=st.session_state["cliente_otros_nombres"], key="occ_otros_nom")
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            primer_apellido = st.text_input("Primer Apellido", value=st.session_state["cliente_primer_apellido"], key="occ_primer_apell")
        with c_a2:
            segundo_apellido = st.text_input("Segundo Apellido", value=st.session_state["cliente_segundo_apellido"], key="occ_seg_apell")
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            cred_trad_opt = st.selectbox(
                "¿CrediOro Tradicional?",
                options=["SI", "NO"],
                index=0 if st.session_state["cliente_cred_tradicional"] == "SI" else 1,
                key="occ_cred_trad_sel",
            )
        with c_m2:
            pais_origen = st.text_input("País de Origen", value=st.session_state["cliente_pais_origen"], key="occ_pais_orig")
        _, col_centro, _ = st.columns([1.2, 1, 1.2])
        with col_centro:
            enviar = st.form_submit_button("Enviar", width='stretch', type="primary")

    if not enviar:
        if st.session_state.get("cliente_registrado"):
            st.markdown(
                f"<div class='result-card'><h4>Ficha de Cliente (OCC)</h4>"
                f"<p><strong>Titular:</strong> {st.session_state.get('cliente_nombres')} "
                f"{st.session_state.get('cliente_apellidos')}</p></div>",
                unsafe_allow_html=True,
            )
        return

    if insolvency_blocks():
        st.error("Envío bloqueado: el cliente consultado está en insolvencia. Cambie el documento en el simulador para levantar el bloqueo.")
        return
    if not primer_nombre.strip() or not primer_apellido.strip():
        st.error("Ingrese al menos el primer nombre y primer apellido.")
        return
    if not session_active():
        st.info("Inicie sesión SIIF antes de inyectar OCC.")
        return

    payload = {
        "primer_apellido": primer_apellido.strip(),
        "segundo_apellido": segundo_apellido.strip(),
        "primer_nombre": primer_nombre.strip(),
        "otros_nombres": otros_nombres.strip(),
        "credioro_tradicional": "1" if cred_trad_opt == "SI" else "2",
        "pais_origen": pais_origen.strip() or "CO",
    }
    st.session_state.update(
        {
            "cliente_primer_nombre": payload["primer_nombre"],
            "cliente_otros_nombres": payload["otros_nombres"],
            "cliente_primer_apellido": payload["primer_apellido"],
            "cliente_segundo_apellido": payload["segundo_apellido"],
            "cliente_nombres": f"{payload['primer_nombre']} {payload['otros_nombres']}".strip(),
            "cliente_apellidos": f"{payload['primer_apellido']} {payload['segundo_apellido']}".strip(),
            "cliente_cred_tradicional": cred_trad_opt,
            "cliente_pais_origen": payload["pais_origen"],
            "occ_payload": payload,
        }
    )
    with st.spinner("El Bot inyecta OCC en SIIF..."):
        try:
            response = execute_process("OCC", **payload)
        except BotClientError as exc:
            st.error(str(exc))
            return
    if not response.ok:
        st.error(response.message)
        return
    st.session_state["cliente_registrado"] = True
    try:
        execute_process("CSB")
    except BotClientError:
        pass
    st.success(response.message)
