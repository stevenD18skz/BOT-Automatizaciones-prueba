"""
garantia_ui.py
--------------
Módulo ORG: Registro y Control de Garantías Prendarias en SIIF
- Selección de la pieza de joyería según el Tipo de Oro activo (18k Italiano, 18k Nacional, 16k, 14k, Moneda).
- Inyección automatizada de cantidad y descripción a sus campos correspondientes en SIIF.
- Asignación e inyección del número de Sticker (N0116).
- Captura de fotografía de la prenda (Cámara Web / Archivo) y carga automatizada en el modal de SIIF.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

import streamlit as st

from client.credioro.form_options import (
    PIEZAS_CANONICAS,
    TEJIDOS_JOYAS_CATALOGO,
    TEJIDOS_SELECT_OPTIONS,
    TIPO_ORO_SIMULADOR_OPTS,
    TIPO_ORO_SUFFIX_MAP,
)
from client.credioro.bot_ops import BotClientError, execute_process, insolvency_blocks, render_insolvency_banner, session_active

logger = logging.getLogger("garantia_ui")

# Directorio local para persistir fotografías tomadas antes de la subida por Selenium
from client.credioro.bot_ops import settings
CAPTURAS_DIR = settings.dataset_dir('captures')
CAPTURAS_DIR.mkdir(parents=True, exist_ok=True)

# Ejemplos de descripción por tipo de pieza
EJEMPLOS_PIEZAS = {
    "Anillos": "Anillo con piedra circonia y grabado",
    "Aretes": "Par de aretes tipo candonga",
    "Cadenas": "Cadena estilo tejido eslabón patrio",
    "Dijes": "Dije figura religiosa",
    "Pulseras": "Pulsera tejido barbado con broche",
    "Relojes": "Reloj con pulso en oro",
    "Monedas": "Moneda de oro conmemorativa",
    "Tobilleras": "Tobillera tejido fino",
    "Brazaletes": "Brazalete rígido tallado",
    "Accesorios": "Accesorio broche prendedor",
}


def render_garantia_module():
    """Renderiza la interfaz del Módulo ORG: Registro y Control de Garantías Prendarias."""
    st.markdown('<div class="module-tag">Módulo ORG &bull; Control y Registro de Garantías</div>', unsafe_allow_html=True)
    st.markdown("### Registro de Garantías Prendarias (ORG)")
    st.caption("Control y registro de la pieza de oro por kilataje, asignación de sticker y carga de fotografía en SIIF.")

    render_insolvency_banner()

    solicitud_id = st.session_state.get("solicitud_id") or "SOL-2026-001"
    cliente_doc = st.session_state.get("cliente_num_doc") or "Sin documento"

    # ── 1. Tipo de Oro Activo ────────────────────────────────────────────────
    sim_tipo_oro = st.session_state.get("sim_tipo_oro", "ORO 18 KTS ITALIANO")

    default_idx = 0
    if sim_tipo_oro in TIPO_ORO_SIMULADOR_OPTS:
        default_idx = TIPO_ORO_SIMULADOR_OPTS.index(sim_tipo_oro)

    with st.container(border=True):
        c_top1, c_top2 = st.columns([2, 1])
        with c_top1:
            tipo_oro_sel = st.selectbox(
                "Tipo de Oro de la Prenda",
                options=TIPO_ORO_SIMULADOR_OPTS,
                index=default_idx,
                key="org_tipo_oro_select",
                help="Clasificación de oro según la cotización del simulador SIIF.",
            )
        with c_top2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:6px 12px; font-size:0.84rem; color:#475569;">
                    <b>Solicitud:</b> {solicitud_id} &nbsp;|&nbsp; <b>Cliente:</b> {cliente_doc}
                </div>
                """,
                unsafe_allow_html=True,
            )

    suffix = TIPO_ORO_SUFFIX_MAP.get(tipo_oro_sel, 1)

    # ── 2. Selección de la Pieza de Joyería ────────────────────────────────────
    st.markdown("#### Discriminación de la Pieza de Joyería")
    st.caption("Seleccione la pieza que compone la garantía, su nomenclatura/tejido en SIIF y especifique su descripción.")

    with st.container(border=True):
        c_pieza, c_cant = st.columns([2, 1])
        with c_pieza:
            pieza_sel = st.selectbox(
                "Pieza de Joyería",
                options=PIEZAS_CANONICAS,
                index=2 if "Cadenas" in PIEZAS_CANONICAS else 0,
                key="org_pieza_select",
            )
        with c_cant:
            cantidad_val = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=99,
                value=1,
                step=1,
                key=f"org_cant_{pieza_sel}_{suffix}",
            )

        # Desplegable de Tejido de Joyería / Nomenclatura SIIF
        c_tejido, c_info = st.columns([1.5, 1])
        with c_tejido:
            tejido_sel_str = st.selectbox(
                "Patrón / Tejido de Joyería (Nomenclatura SIIF)",
                options=TEJIDOS_SELECT_OPTIONS,
                index=0,
                key=f"org_tejido_sel_{pieza_sel}_{suffix}",
                help="Seleccione el tejido de la joya para autocompletar la descripción estandarizada según nomenclatura de SIIF.",
            )

        codigo_tejido = tejido_sel_str.split(" — ")[0].strip() if " — " in tejido_sel_str else ""
        info_tejido = TEJIDOS_JOYAS_CATALOGO.get(codigo_tejido)

        with c_info:
            if info_tejido:
                st.markdown(
                    f"""
                    <div style="background:#EBF9FD; border:1.5px solid #C2EEFA; border-radius:10px; padding:7px 12px; margin-top:22px; font-size:0.8rem; color:#0FA8CC;">
                        <b>Código SIIF:</b> <span class="cat-badge" style="padding:2px 8px; font-size:0.75rem;">{info_tejido['codigo']}</span>
                        <div style="font-size:0.75rem; color:#4A6278; margin-top:2px;">{info_tejido['nombre']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
                st.caption("ℹ️ Opcional: Estandariza la descripción para Cadenas, Pulseras, Dijes, etc.")

        # Generar texto de sugerencia base para la descripción
        nombre_singular = pieza_sel[:-1] if pieza_sel.endswith("s") and len(pieza_sel) > 3 else pieza_sel
        if info_tejido:
            nombre_limpio = info_tejido['nombre'].replace("Tejido ", "").lower()
            sugerencia_desc = f"{nombre_singular} tejido {nombre_limpio} ({info_tejido['codigo']})"
        else:
            sugerencia_desc = EJEMPLOS_PIEZAS.get(pieza_sel, "Descripción detallada de la prenda")

        descripcion_val = st.text_input(
            f"Descripción de {pieza_sel} (Texto inyectado a SIIF)",
            value=sugerencia_desc,
            placeholder=f"Ej: {sugerencia_desc}",
            key=f"org_desc_{pieza_sel}_{suffix}_{codigo_tejido}",
            help="Descripción final que se enviará a SIIF en el campo de la prenda.",
        )

        if info_tejido:
            st.caption(f"💡 **Características del {info_tejido['nombre']} ({info_tejido['codigo']}):** {info_tejido['descripcion']}")

    # ── 3. Asignación del Sticker de Custodia ──────────────────────────────────
    st.markdown("#### Número de Sticker de Custodia")

    col_stk, _ = st.columns([2, 1])
    with col_stk:
        sticker_val = st.text_input(
            "Número de Sticker / Etiqueta Física",
            value=st.session_state.get("org_sticker_val", f"STK-2026-{solicitud_id[-4:] if len(solicitud_id) >= 4 else '001'}"),
            placeholder="Ej: STK-2026-00912",
            key="org_input_sticker",
        )

    # ── 4. Registro y Captura de Fotografía de la Prenda ──────────────────────
    st.markdown("#### Registro Fotográfico de la Prenda")
    st.caption("Capture la foto en vivo o adjunte un archivo para la carga en el portal SIIF.")

    tab_cam, tab_arch = st.tabs(["Tomar Foto con Cámara Web", "Adjuntar Archivo desde PC"])
    foto_bytes = None
    foto_nombre = None

    with tab_cam:
        if "org_camera_enabled" not in st.session_state:
            st.session_state["org_camera_enabled"] = False

        col_cam_view, col_cam_guide = st.columns([1.2, 1])
        with col_cam_view:
            if st.button(
                "Activar cámara web" if not st.session_state["org_camera_enabled"] else "Desactivar cámara web",
                key="org_toggle_camera",
                width='stretch',
            ):
                st.session_state["org_camera_enabled"] = not st.session_state["org_camera_enabled"]

            if st.session_state["org_camera_enabled"]:
                cam_input = st.camera_input("Capturar fotografía de la joya en vivo", key="org_camera_input")
                if cam_input:
                    foto_bytes = cam_input.getvalue()
                    foto_nombre = f"FOTO_{solicitud_id}_{int(time.time())}.jpg"
            else:
                st.info("La cámara no se activa hasta que usted presione el botón de activación.")
                cam_input = None
        with col_cam_guide:
            st.markdown(
                """
                <div style="background:#F8FAFC; border:1px solid #E2EAF0; border-radius:10px; padding:14px; margin-top:8px;">
                    <h5 style="margin:0 0 6px; font-size:0.88rem; color:#1A2B3C; font-weight:700;">Guía de Carga en SIIF</h5>
                    <ol style="margin:0; padding-left:18px; font-size:0.82rem; color:#4A6278; line-height:1.6;">
                        <li>Apertura del módulo de carga de fotos.</li>
                        <li>Selección de opción IMAGEN JOYA.</li>
                        <li>Adjunto del archivo de fotografía.</li>
                        <li>Confirmación de subida en el portal.</li>
                    </ol>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_arch:
        arch_input = st.file_uploader(
            "Seleccionar archivo de imagen de la prenda",
            type=["jpg", "jpeg", "png"],
            key="org_file_uploader",
        )
        if arch_input and not foto_bytes:
            foto_bytes = arch_input.getvalue()
            foto_nombre = arch_input.name

    # Guardar foto localmente si fue capturada
    local_foto_path = ""
    if foto_bytes:
        nombre_guardar = f"{solicitud_id}_{foto_nombre or 'prenda.jpg'}"
        guardado_path = CAPTURAS_DIR / nombre_guardar
        guardado_path.write_bytes(foto_bytes)
        local_foto_path = str(guardado_path.resolve())
        st.session_state["org_ultima_foto_path"] = local_foto_path
        st.success(f"Fotografía guardada correctamente: {guardado_path.name}")
    elif st.session_state.get("org_ultima_foto_path") and os.path.isfile(st.session_state["org_ultima_foto_path"]):
        local_foto_path = st.session_state["org_ultima_foto_path"]

    # ── 5. Acciones de Inyección en SIIF ──────────────────────────────────────
    st.markdown("---")
    col_izq, col_centro, col_der = st.columns([1, 1.8, 1])

    with col_centro:
        btn_inyectar_siif = st.button(
            "Inyectar Garantía y Cargar Foto en SIIF (ORG)",
            type="primary",
            width='stretch',
            key="btn_org_inyectar_siif",
        )

    # ── Ejecución Selenium en SIIF ────────────────────────────────────────────
    if btn_inyectar_siif:
        if insolvency_blocks():
            st.error("Envío bloqueado: el cliente consultado está en insolvencia.")
        elif not session_active():
            st.info("Inicie sesión SIIF antes de inyectar la garantía.")
        else:
            with st.spinner("El Bot inyecta pieza, sticker y fotografía en SIIF..."):
                try:
                    response = execute_process(
                        "ORG",
                        solicitud_id=solicitud_id,
                        tipo_oro=tipo_oro_sel,
                        pieza=pieza_sel,
                        cantidad=cantidad_val,
                        descripcion=descripcion_val.strip(),
                        sticker=sticker_val,
                        foto_path=local_foto_path,
                        enviar_formulario=True,
                    )
                except BotClientError as exc:
                    st.error(str(exc))
                    response = None
            if response is not None:
                if response.ok:
                    st.success(response.message)
                    st.session_state["org_completado"] = True
                else:
                    st.error(response.message)

    # ── 6. Resumen de la Garantía Registrada ──────────────────────────────────
    st.markdown("---")
    st.markdown("#### Resumen de la Garantía Prendaria")

    resumen_data = [{
        "Tipo de Oro": tipo_oro_sel,
        "Pieza": pieza_sel,
        "Cantidad": cantidad_val,
        "Descripción": descripcion_val.strip(),
        "Sticker": sticker_val,
        "Fotografía": Path(local_foto_path).name if local_foto_path else "Sin Fotografía",
    }]
    st.dataframe(resumen_data, width='stretch')

    c_r1, c_r2, c_r3 = st.columns(3)
    with c_r1:
        st.metric("Pieza y Cantidad", f"{pieza_sel} (x{cantidad_val})")
    with c_r2:
        st.metric("Sticker Asignado", sticker_val or "N/A")
    with c_r3:
        st.metric("Estado de Fotografía", "Foto Adjunta" if local_foto_path else "Sin Fotografía")
