"""
oif_ui.py
---------
Módulo OIF: Captura de Información Financiera del Cliente en SIIF.
- Formulario con fecha de nacimiento, datos socioeconómicos, ingresos, gastos y patrimonio.
- Los desplegables muestran texto descriptivo e inyectan en SIIF el código numérico correspondiente.
- Soporta modo con/sin sesión Selenium activa.
"""

from __future__ import annotations

import logging
from datetime import date

import streamlit as st

from client.credioro.form_options import (
    TIPO_VIVIENDA_OPTS,
    ESTADO_CIVIL_OPTS,
    PERSONAS_CARGO_OPTS,
    ESTRATO_OPTS,
    NIVEL_ESTUDIOS_OPTS,
    OCUPACION_OPTS,
    TIPO_CONTRATO_OPTS,
    ANTIGUEDAD_OPTS,
)
from client.credioro.bot_ops import (
    BotClientError,
    execute_process,
    insolvency_blocks,
    render_insolvency_banner,
    session_active,
)

logger = logging.getLogger("oif_ui")


def _idx(lst: list, val) -> int:
    """Retorna el índice de val en lst; retorna 0 si no se encuentra."""
    try:
        return lst.index(val)
    except ValueError:
        return 0


def _siif_help(campo_key: str, extra: str = "") -> str:
    """Devuelve el texto de ayuda con el ID del campo en SIIF o el nombre del selector."""
    MENU_ROUTE_CREDIORO: dict = {}  # maqueta: sin selectores SIIF
    id_val = str(MENU_ROUTE_CREDIORO.get(campo_key, "")).strip()
    base = f"Campo {id_val} del SIIF" if id_val else f"Campo SIIF: {campo_key}"
    return f"{base} ({extra})" if extra else base


def render_oif_module():
    """Renderiza la interfaz del Módulo OIF: Captura de Información Financiera."""
    st.markdown(
        '<div class="module-tag">Módulo OIF &bull; Información Financiera</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Captura de Información Financiera (OIF)")
    st.caption(
        "Diligencia los datos socioecónomicos, ingresos, gastos y patrimonio del cliente. "
        "Los desplegables muestran el nombre y envían el código numérico al portal SIIF."
    )
    render_insolvency_banner()

    # Listas de claves para los selectboxes
    _VIV_LIST  = list(TIPO_VIVIENDA_OPTS.keys())
    _CIV_LIST  = list(ESTADO_CIVIL_OPTS.keys())
    _PER_LIST  = list(PERSONAS_CARGO_OPTS.keys())
    _EST_LIST  = list(ESTRATO_OPTS.keys())
    _NIV_LIST  = list(NIVEL_ESTUDIOS_OPTS.keys())
    _OCP_LIST  = list(OCUPACION_OPTS.keys())
    _CNT_LIST  = list(TIPO_CONTRATO_OPTS.keys())
    _ANT_LIST  = list(ANTIGUEDAD_OPTS.keys())

    # ── Inicializar session_state ─────────────────────────────────────────────
    defaults = {
        "oif_fecha_nacimiento":      date(1990, 1, 1),
        "oif_tipo_vivienda":         "1",
        "oif_estado_civil":          "1",
        "oif_personas_cargo":        "0",
        "oif_estrato":               "1",
        "oif_nivel_estudios":        "2",
        "oif_ocupacion":             "1",
        "oif_tipo_contrato":         "2",
        "oif_antiguedad":            "2",
        "oif_salario_honorarios":    "",
        "oif_arrendamientos":        "",
        "oif_otros_ingresos":        "",
        "oif_origen_otros_ingresos": "",
        "oif_gastos_familiares":     "",
        "oif_gastos_financieros":    "",
        "oif_otros_gastos":          "",
        "oif_detalle_otros_gastos":  "",
        "oif_total_activos":         "",
        "oif_total_pasivos":         "",
        "oif_observaciones":         "",
        "oif_completado":            False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    solicitud_id = str(st.session_state.get("solicitud_id") or "SOL-OIF-001")

    # Tarjeta de estado completado
    if st.session_state.get("oif_completado"):
        st.markdown(
            """
            <div style="background:#E8F8F5;border:1px solid #2ECC71;border-radius:8px;
                        padding:12px 16px;margin-bottom:16px;">
                <strong style="color:#27AE60;">Proceso OIF Completado con Exito</strong><br>
                <span style="font-size:0.85rem;color:#2C3E50;">
                    La información financiera del cliente fue registrada en SIIF.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── FORMULARIO ────────────────────────────────────────────────────────────
    with st.form("form_oif_financiero", clear_on_submit=False):

        # ── Bloque 1: Datos Personales / Socioeconómicos ──────────────────────
        st.markdown("#### Datos Personales y Socioeconomicos")
        c1, c2, c3 = st.columns(3)
        with c1:
            fecha_nac = st.date_input(
                "Fecha de Nacimiento",
                value=st.session_state.get("oif_fecha_nacimiento", date(1990, 1, 1)),
                min_value=date(1920, 1, 1),
                max_value=date.today(),
                format="YYYY/MM/DD",
                key="oif_input_fecha_nac",
                help=_siif_help("FechaDeNacimiento", "formato AAAAMMDD"),
            )
        with c2:
            tipo_vivienda = st.selectbox(
                "Tipo de Vivienda",
                options=_VIV_LIST,
                format_func=lambda k: TIPO_VIVIENDA_OPTS.get(k, k),
                index=_idx(_VIV_LIST, st.session_state.get("oif_tipo_vivienda", "1")),
                key="oif_sel_vivienda",
                help=_siif_help("TipoDeVivienda", "1=PROPIA · 2=ALQUILADA < 1 AÑO · 3=ALQUILADA > 1 AÑO · 4=FAMILIAR"),
            )
        with c3:
            estado_civil = st.selectbox(
                "Estado Civil",
                options=_CIV_LIST,
                format_func=lambda k: ESTADO_CIVIL_OPTS.get(k, k),
                index=_idx(_CIV_LIST, st.session_state.get("oif_estado_civil", "1")),
                key="oif_sel_estado_civil",
                help=_siif_help("EstadoCivil", "1=SOLTERO · 2=CASADO · 3=SEPARADO · 4=DIVORCIADO · 5=VIUDO · 6=RELIGIOSO · 7=UNIÓN LIBRE"),
            )

        c4, c5, c6 = st.columns(3)
        with c4:
            personas_cargo = st.selectbox(
                "Personas a Cargo",
                options=_PER_LIST,
                format_func=lambda k: PERSONAS_CARGO_OPTS.get(k, k),
                index=_idx(_PER_LIST, st.session_state.get("oif_personas_cargo", "0")),
                key="oif_sel_personas_cargo",
                help=_siif_help("PersonasACargo", "0=0 · 1=1 · 2=2 · 3=3 · 4=4 · 5=MÁS DE 4"),
            )
        with c5:
            estrato = st.selectbox(
                "Estrato",
                options=_EST_LIST,
                format_func=lambda k: ESTRATO_OPTS.get(k, k),
                index=_idx(_EST_LIST, st.session_state.get("oif_estrato", "1")),
                key="oif_sel_estrato",
                help=_siif_help("Estrato", "valores 1 al 6"),
            )
        with c6:
            nivel_estudios = st.selectbox(
                "Nivel de Estudios",
                options=_NIV_LIST,
                format_func=lambda k: NIVEL_ESTUDIOS_OPTS.get(k, k),
                index=_idx(_NIV_LIST, st.session_state.get("oif_nivel_estudios", "2")),
                key="oif_sel_nivel_estudios",
                help=_siif_help("NivelDeEstudios", "1=PRIMARIA · 2=BACHILLERATO · 3=TÉCNICO · 4=TECNÓLOGO · 5=UNIVERSITARIO"),
            )

        c7, c8, c9 = st.columns(3)
        with c7:
            ocupacion = st.selectbox(
                "Ocupación",
                options=_OCP_LIST,
                format_func=lambda k: OCUPACION_OPTS.get(k, k),
                index=_idx(_OCP_LIST, st.session_state.get("oif_ocupacion", "1")),
                key="oif_sel_ocupacion",
                help=_siif_help("Ocupacion", "1=EMPLEADO · 2=INDEPENDIENTE · 3=INDEP. EMPRESA · 4=TRANSPORTADOR · 5=PENSIONADO · 6=RENTISTA · 7=AMA DE CASA · 8=ESTUDIANTE · 9=SIN OCUPACIÓN"),
            )
        with c8:
            tipo_contrato = st.selectbox(
                "Tipo de Contrato",
                options=_CNT_LIST,
                format_func=lambda k: TIPO_CONTRATO_OPTS.get(k, k),
                index=_idx(_CNT_LIST, st.session_state.get("oif_tipo_contrato", "2")),
                key="oif_sel_tipo_contrato",
                help=_siif_help("TipoDeContrato", "1=FIJO · 2=INDEFINIDO · 3=TEMPORAL"),
            )
        with c9:
            antiguedad = st.selectbox(
                "Antigüedad Actividad Económica",
                options=_ANT_LIST,
                format_func=lambda k: ANTIGUEDAD_OPTS.get(k, k),
                index=_idx(_ANT_LIST, st.session_state.get("oif_antiguedad", "2")),
                key="oif_sel_antiguedad",
                help=_siif_help("AntiguedadActividadEconomica", "1=MENOR A 1 AÑO · 2=ENTRE 1 Y 6 AÑOS · 3=MAYOR A 6 AÑOS"),
            )

        st.markdown("---")

        # ── Bloque 2: Ingresos ────────────────────────────────────────────────
        st.markdown("#### Ingresos Mensuales")
        ci1, ci2, ci3, ci4 = st.columns(4)
        with ci1:
            salario = st.text_input(
                "Salario / Honorarios ($)",
                value=st.session_state.get("oif_salario_honorarios", ""),
                placeholder="Ej: 2500000",
                key="oif_inp_salario",
                help=_siif_help("SalarioHonorarios"),
            )
        with ci2:
            arrendamientos = st.text_input(
                "Arrendamientos ($)",
                value=st.session_state.get("oif_arrendamientos", ""),
                placeholder="Ej: 500000",
                key="oif_inp_arrendamientos",
                help=_siif_help("Arrendamientos"),
            )
        with ci3:
            otros_ingresos = st.text_input(
                "Otros Ingresos ($)",
                value=st.session_state.get("oif_otros_ingresos", ""),
                placeholder="Ej: 200000",
                key="oif_inp_otros_ingresos",
                help=_siif_help("OtrosIngresos"),
            )
        with ci4:
            origen_otros = st.text_input(
                "Origen Otros Ingresos",
                value=st.session_state.get("oif_origen_otros_ingresos", ""),
                placeholder="Ej: Arriendos, dividendos...",
                key="oif_inp_origen_otros",
                help=_siif_help("OrigenOtrosIngresos"),
            )

        st.markdown("---")

        # ── Bloque 3: Gastos ──────────────────────────────────────────────────
        st.markdown("#### Gastos Mensuales")
        cg1, cg2, cg3, cg4 = st.columns(4)
        with cg1:
            gastos_fam = st.text_input(
                "Gastos Familiares ($)",
                value=st.session_state.get("oif_gastos_familiares", ""),
                placeholder="Ej: 1000000",
                key="oif_inp_gastos_fam",
                help=_siif_help("GastosFamiliares"),
            )
        with cg2:
            gastos_fin = st.text_input(
                "Gastos Financieros ($)",
                value=st.session_state.get("oif_gastos_financieros", ""),
                placeholder="Ej: 300000",
                key="oif_inp_gastos_fin",
                help=_siif_help("GastosFinancieros"),
            )
        with cg3:
            otros_gastos = st.text_input(
                "Otros Gastos ($)",
                value=st.session_state.get("oif_otros_gastos", ""),
                placeholder="Ej: 100000",
                key="oif_inp_otros_gastos",
                help=_siif_help("OtrosGastos"),
            )
        with cg4:
            detalle_otros_gastos = st.text_input(
                "Detalle Otros Gastos",
                value=st.session_state.get("oif_detalle_otros_gastos", ""),
                placeholder="Ej: Educación, salud...",
                key="oif_inp_detalle_otros_gastos",
                help=_siif_help("DetalleOtrosGastos"),
            )

        st.markdown("---")

        # ── Bloque 4: Patrimonio y Observaciones ──────────────────────────────
        st.markdown("#### Patrimonio y Observaciones")
        cp1, cp2, cp3 = st.columns([1, 1, 2])
        with cp1:
            total_activos = st.text_input(
                "Total Activos ($)",
                value=st.session_state.get("oif_total_activos", ""),
                placeholder="Ej: 15000000",
                key="oif_inp_activos",
                help=_siif_help("TotalActivos"),
            )
        with cp2:
            total_pasivos = st.text_input(
                "Total Pasivos ($)",
                value=st.session_state.get("oif_total_pasivos", ""),
                placeholder="Ej: 5000000",
                key="oif_inp_pasivos",
                help=_siif_help("TotalPasivos"),
            )
        with cp3:
            observaciones = st.text_input(
                "Observaciones",
                value=st.session_state.get("oif_observaciones", ""),
                placeholder="Observaciones adicionales para SIIF...",
                key="oif_inp_observaciones",
                help=_siif_help("Observaciones"),
            )

        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # ── Botón de Envío centrado ───────────────────────────────────────────
        col_izq, col_btn, col_der = st.columns([1.2, 1, 1.2])
        with col_btn:
            enviar_oif = st.form_submit_button(
                "Enviar",
                width='stretch',
                type="primary",
            )

    # ── Lógica de Envío ───────────────────────────────────────────────────────
    if enviar_oif:
        # Formatear fecha AAAAMMDD
        fecha_aaaammdd = fecha_nac.strftime("%Y%m%d")

        # Guardar en session_state
        st.session_state.update({
            "oif_fecha_nacimiento":      fecha_nac,
            "oif_tipo_vivienda":         tipo_vivienda,
            "oif_estado_civil":          estado_civil,
            "oif_personas_cargo":        personas_cargo,
            "oif_estrato":               estrato,
            "oif_nivel_estudios":        nivel_estudios,
            "oif_ocupacion":             ocupacion,
            "oif_tipo_contrato":         tipo_contrato,
            "oif_antiguedad":            antiguedad,
            "oif_salario_honorarios":    salario.strip(),
            "oif_arrendamientos":        arrendamientos.strip(),
            "oif_otros_ingresos":        otros_ingresos.strip(),
            "oif_origen_otros_ingresos": origen_otros.strip(),
            "oif_gastos_familiares":     gastos_fam.strip(),
            "oif_gastos_financieros":    gastos_fin.strip(),
            "oif_otros_gastos":          otros_gastos.strip(),
            "oif_detalle_otros_gastos":  detalle_otros_gastos.strip(),
            "oif_total_activos":         total_activos.strip(),
            "oif_total_pasivos":         total_pasivos.strip(),
            "oif_observaciones":         observaciones.strip(),
        })

        if insolvency_blocks():
            st.error("Envío bloqueado: el cliente consultado está en insolvencia. Cambie el documento en el simulador para levantar el bloqueo.")
            return
        if not session_active():
            st.info("Inicie sesión SIIF antes de inyectar OIF.")
            return
        with st.spinner("El Bot inyecta información financiera en SIIF (OIF)..."):
            try:
                response = execute_process(
                    "OIF",
                    solicitud_id=solicitud_id,
                    fecha_nacimiento=fecha_aaaammdd,
                    tipo_vivienda=tipo_vivienda,
                    estado_civil=estado_civil,
                    personas_cargo=personas_cargo,
                    estrato=estrato,
                    nivel_estudios=nivel_estudios,
                    ocupacion=ocupacion,
                    tipo_contrato=tipo_contrato,
                    antiguedad=antiguedad,
                    salario_honorarios=salario.strip(),
                    arrendamientos=arrendamientos.strip(),
                    otros_ingresos=otros_ingresos.strip(),
                    origen_otros_ingresos=origen_otros.strip(),
                    gastos_familiares=gastos_fam.strip(),
                    gastos_financieros=gastos_fin.strip(),
                    otros_gastos=otros_gastos.strip(),
                    detalle_otros_gastos=detalle_otros_gastos.strip(),
                    total_activos=total_activos.strip(),
                    total_pasivos=total_pasivos.strip(),
                    observaciones=observaciones.strip(),
                    enviar_formulario=True,
                )
            except BotClientError as exc:
                st.error(str(exc))
                return
        if response.ok:
            st.session_state["oif_completado"] = True
            st.success(response.message)
            st.rerun()
        else:
            st.error(response.message)
