"""
ova_ui.py
---------
Módulo OVA: Vinculación de Tercero Autorizado / Beneficiario en SIIF
- Captura o lectura automatizada de datos desde el portal SIIF.
- Formulario de edición: Identificación, Nombre Completo y Parentesco.
- Inyección automatizada en SIIF y envío mediante el botón Enviar5 con aceptación de alerta.
- Persistencia local en SQLite para trazabilidad y auditoría.
"""

from __future__ import annotations

import logging
import streamlit as st

from client.credioro.form_options import PARENTESCO_OPTS, TEXTO_TO_PARENTESCO_CODE
from client.credioro.bot_ops import BotClientError, execute_process, insolvency_blocks, render_insolvency_banner, session_active

logger = logging.getLogger("ova_ui")


def populate_ova_from_siif(datos: dict[str, str]) -> None:
    """
    Actualiza el session_state del módulo OVA con los datos detectados desde el portal SIIF.
    """
    if not datos:
        return

    if "identificacion" in datos and datos["identificacion"]:
        st.session_state["ova_identificacion"] = datos["identificacion"]
    if "nombre_completo" in datos and datos["nombre_completo"]:
        st.session_state["ova_nombre_completo"] = datos["nombre_completo"]
    if "parentesco" in datos and datos["parentesco"]:
        raw_par = str(datos["parentesco"]).strip()
        # Si vino el texto en lugar del código, convertir a código
        code = TEXTO_TO_PARENTESCO_CODE.get(raw_par, raw_par)
        if code in PARENTESCO_OPTS:
            st.session_state["ova_parentesco"] = code
        else:
            st.session_state["ova_parentesco"] = "1"



def render_ova_module():
    """Renderiza la interfaz del Módulo OVA: Vinculación de Beneficiario / Autorizado."""
    st.markdown(
        '<div class="module-tag">Módulo OVA &bull; Vinculación Autorizado</div>',
        unsafe_allow_html=True,
    )

    render_insolvency_banner()

    # ── Inicializar session_state para OVA ────────────────────────────────────
    if "ova_identificacion" not in st.session_state:
        st.session_state["ova_identificacion"] = ""
    if "ova_nombre_completo" not in st.session_state:
        st.session_state["ova_nombre_completo"] = ""
    if "ova_parentesco" not in st.session_state:
        st.session_state["ova_parentesco"] = "5"  # HIJO(A) por defecto
    if "ova_completado" not in st.session_state:
        st.session_state["ova_completado"] = False
    if "ova_ultimo_resultado" not in st.session_state:
        st.session_state["ova_ultimo_resultado"] = None

    solicitud_id = str(st.session_state.get("solicitud_id") or "SOL-OVA-001")

    st.markdown("### Vinculación de Tercero Autorizado / Beneficiario (OVA)")
    st.caption(
        "Registro de datos del beneficiario o tercero autorizado (Identificación, Nombre Completo y Parentesco) "
        "en el portal SIIF."
    )

    if session_active() and not st.session_state.get("ova_auto_cargado"):
        st.session_state["ova_auto_cargado"] = True
        if not insolvency_blocks():
            try:
                response = execute_process("OVA", action="read")
                datos = (response.data or {}).get("fields") or {}
                if response.ok and any(datos.values()):
                    populate_ova_from_siif(datos)
            except Exception:
                pass


    # ── Tarjeta Informativa de Estado ─────────────────────────────────────────
    if st.session_state.get("ova_completado"):
        res = st.session_state.get("ova_ultimo_resultado") or {}
        st.markdown(
            f"""
            <div style="background:#E8F8F5;border:1px solid #2ECC71;border-radius:8px;padding:12px 16px;margin-bottom:16px;">
                <strong style="color:#27AE60;">✅ Proceso OVA Completado con Éxito</strong><br>
                <span style="font-size:0.85rem;color:#2C3E50;">
                    Beneficiario registrado: <strong>{res.get('nombre_completo', '—')}</strong> |
                    Doc: <strong>{res.get('identificacion', '—')}</strong> |
                    Parentesco: <strong>{res.get('parentesco_texto', res.get('parentesco', '—'))}</strong>
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Formulario de Beneficiario OVA ───────────────────────────────────────
    with st.form("form_ova_beneficiario", clear_on_submit=False):
        st.markdown("#### Datos del Beneficiario / Autorizado")

        # Fila Única: Identificación, Nombre Completo y Parentesco en 3 columnas seguidas
        c_id, c_nom, c_par = st.columns([1.1, 2.0, 1.3])
        with c_id:
            identificacion_val = st.text_input(
                "1. Identificación Beneficiario",
                value=st.session_state.get("ova_identificacion", ""),
                placeholder="Ej: 1098765432",
                key="ova_input_identificacion",
                help="Campo N0001 del portal SIIF — Cédula o documento del tercero autorizado",
            )

        with c_nom:
            nombre_completo_val = st.text_input(
                "2. Nombre Completo Beneficiario",
                value=st.session_state.get("ova_nombre_completo", ""),
                placeholder="Ej: María Camila Rodríguez Gómez",
                key="ova_input_nombre_completo",
                help="Campo N0002 del portal SIIF — Nombre completo del tercero autorizado",
            )

        with c_par:
            keys_par = list(PARENTESCO_OPTS.keys())
            current_par = str(st.session_state.get("ova_parentesco", "5")).strip()
            if current_par in TEXTO_TO_PARENTESCO_CODE:
                current_par = TEXTO_TO_PARENTESCO_CODE[current_par]
            idx_par = keys_par.index(current_par) if current_par in keys_par else 4  # default HIJO(A)

            parentesco_code_sel = st.selectbox(
                "3. Parentesco / Relación",
                options=keys_par,
                format_func=lambda k: PARENTESCO_OPTS.get(k, k),
                index=idx_par,
                key="ova_select_parentesco",
                help="Campo N0003 del portal SIIF — Se inyectará el código numérico correspondiente en SIIF",
            )

        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # Botón de Envío
        col_izq, col_centro, col_der = st.columns([1.2, 1, 1.2])
        with col_centro:
            enviar_ova = st.form_submit_button(
                "Enviar",
                width='stretch',
                type="primary",
            )

    # ── Lógica de Envío e Inyección ──────────────────────────────────────────
    if enviar_ova:
        id_clean = identificacion_val.strip()
        nom_clean = nombre_completo_val.strip()
        par_code = str(parentesco_code_sel).strip()
        par_texto = PARENTESCO_OPTS.get(par_code, par_code)

        # Validaciones locales previas
        errores = []
        if not id_clean:
            errores.append("La Identificación del Beneficiario (N0001) es obligatoria.")
        if not nom_clean:
            errores.append("El Nombre Completo del Beneficiario (N0002) es obligatorio.")

        if errores:
            for err in errores:
                st.error(f"❌ {err}")
        else:
            # Guardar en session_state
            st.session_state["ova_identificacion"] = id_clean
            st.session_state["ova_nombre_completo"] = nom_clean
            st.session_state["ova_parentesco"] = par_code

            if insolvency_blocks():
                st.error("Envío bloqueado: el cliente consultado está en insolvencia.")
            elif not session_active():
                st.info("Inicie sesión SIIF antes de inyectar OVA.")
            else:
                with st.spinner("El Bot inyecta el beneficiario en SIIF (OVA)..."):
                    try:
                        response = execute_process(
                            "OVA",
                            solicitud_id=solicitud_id,
                            identificacion=id_clean,
                            nombre_completo=nom_clean,
                            parentesco=par_code,
                            enviar_formulario=True,
                        )
                    except BotClientError as exc:
                        st.error(str(exc))
                        response = None
                if response is not None and response.ok:
                    st.session_state["ova_completado"] = True
                    st.session_state["ova_ultimo_resultado"] = {
                        "identificacion": id_clean,
                        "nombre_completo": nom_clean,
                        "parentesco": par_code,
                        "parentesco_texto": par_texto,
                        "mensaje": response.message,
                    }
                    try:
                        execute_process("PID", solicitud_id=solicitud_id, total_documentos=4)
                    except BotClientError:
                        pass
                    st.success(response.message)
                    st.rerun()
                elif response is not None:
                    st.error(response.message)
