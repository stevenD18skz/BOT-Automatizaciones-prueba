"""
ovb_ui.py
---------
Módulo OVB: Vinculación del Cliente
- Captura de datos de nacimiento, nacionalidad, expedición de documento,
  residencia, género, contacto, ocupación, fiscal y referencias.
- Soporta captura/lectura automática de campos pre-cargados en SIIF.
- Usa diccionarios DANE para municipios: nombre visible en el front y código DANE inyectado en SIIF.
"""

from datetime import date
import streamlit as st

from client.credioro.bot_ops import BotClientError, execute_process, insolvency_blocks, render_insolvency_banner, session_active

from client.credioro.form_options import (
    MUNICIPIOS_DANE,
    DANE_TO_MUNICIPIO,
    TIPO_NACIONALIDAD_OPTS,
    PAIS_OPTS,
    GENERO_OPTS,
    DETALLE_ACTIVIDAD_OPTS,
    CARGO_OPTS,
    SI_NO_SIIF_OPTS,
)


# Listas ordenadas para los selectboxes
_MUNICIPIOS_LIST = sorted(MUNICIPIOS_DANE.keys())
_PAIS_LIST       = list(PAIS_OPTS.keys())                # ["CO"]
_NAC_LIST        = list(TIPO_NACIONALIDAD_OPTS.keys())   # ["1", "2"]
_GENERO_LIST     = list(GENERO_OPTS.keys())              # ["1","2","3","4"]
_ACT_LIST        = list(DETALLE_ACTIVIDAD_OPTS.keys())   # ["1"..."7"]
_CARGO_LIST      = list(CARGO_OPTS.keys())               # ["1"..."99"]
_SINO_LIST       = list(SI_NO_SIIF_OPTS.keys())          # ["1","2"]


def _idx(lst: list, val) -> int:
    """Devuelve el índice de val en lst; si no existe retorna 0."""
    try:
        return lst.index(val)
    except ValueError:
        return 0


def populate_ovb_from_siif(datos: dict[str, str]) -> None:
    """
    Actualiza el session_state del front con los datos leídos/capturados desde el portal SIIF.
    Convierte códigos DANE a nombres de ciudades y cadenas AAAAMMDD a objetos date.
    """
    if not datos:
        return

    if "ciudad_nacimiento" in datos and datos["ciudad_nacimiento"]:
        code = datos["ciudad_nacimiento"]
        st.session_state["ovb_ciudad_nacimiento"] = DANE_TO_MUNICIPIO.get(code, code)
    if "tipo_nacionalidad" in datos and datos["tipo_nacionalidad"]:
        st.session_state["ovb_tipo_nacionalidad"] = datos["tipo_nacionalidad"]
    if "pais_expedicion" in datos and datos["pais_expedicion"]:
        st.session_state["ovb_pais_expedicion"] = datos["pais_expedicion"]
    if "ciudad_expedicion" in datos and datos["ciudad_expedicion"]:
        code = datos["ciudad_expedicion"]
        st.session_state["ovb_ciudad_expedicion"] = DANE_TO_MUNICIPIO.get(code, code)
    if "fecha_expedicion" in datos and datos["fecha_expedicion"]:
        f_raw = datos["fecha_expedicion"].replace("-", "").replace("/", "")
        try:
            if len(f_raw) == 8 and f_raw.isdigit():
                st.session_state["ovb_fecha_expedicion"] = date(int(f_raw[:4]), int(f_raw[4:6]), int(f_raw[6:8]))
        except Exception:
            pass
    if "genero" in datos and datos["genero"]:
        st.session_state["ovb_genero"] = datos["genero"]
    if "pais_domicilio" in datos and datos["pais_domicilio"]:
        st.session_state["ovb_pais_domicilio"] = datos["pais_domicilio"]
    if "ciudad_residencia" in datos and datos["ciudad_residencia"]:
        code = datos["ciudad_residencia"]
        st.session_state["ovb_ciudad_residencia"] = DANE_TO_MUNICIPIO.get(code, code)
    if "direccion_residencia" in datos and datos["direccion_residencia"]:
        st.session_state["ovb_direccion_residencia"] = datos["direccion_residencia"]
    if "barrio" in datos and datos["barrio"]:
        st.session_state["ovb_barrio"] = datos["barrio"]
    if "celular" in datos and datos["celular"]:
        st.session_state["ovb_celular"] = datos["celular"]
    if "profesion" in datos and datos["profesion"]:
        st.session_state["ovb_profesion"] = datos["profesion"]
    if "correo" in datos and datos["correo"]:
        st.session_state["ovb_correo"] = datos["correo"]
    if "nombre_empresa" in datos and datos["nombre_empresa"]:
        st.session_state["ovb_nombre_empresa"] = datos["nombre_empresa"]
    if "dir_empresa" in datos and datos["dir_empresa"]:
        st.session_state["ovb_dir_empresa"] = datos["dir_empresa"]
    if "tel_empresa" in datos and datos["tel_empresa"]:
        st.session_state["ovb_tel_empresa"] = datos["tel_empresa"]
    if "ciudad_empresa" in datos and datos["ciudad_empresa"]:
        code = datos["ciudad_empresa"]
        st.session_state["ovb_ciudad_empresa"] = DANE_TO_MUNICIPIO.get(code, code)
    if "detalle_actividad" in datos and datos["detalle_actividad"]:
        st.session_state["ovb_detalle_actividad"] = datos["detalle_actividad"]
    if "cargo" in datos and datos["cargo"]:
        st.session_state["ovb_cargo"] = datos["cargo"]
    if "declara_renta" in datos and datos["declara_renta"]:
        st.session_state["ovb_declara_renta"] = datos["declara_renta"]
    if "contabilidad" in datos and datos["contabilidad"]:
        st.session_state["ovb_contabilidad"] = datos["contabilidad"]
    if "dir_reporte" in datos and datos["dir_reporte"]:
        st.session_state["ovb_dir_reporte"] = datos["dir_reporte"]
    if "origen_fondos" in datos and datos["origen_fondos"]:
        st.session_state["ovb_origen_fondos"] = datos["origen_fondos"]
    if "ref_pers_nombre" in datos and datos["ref_pers_nombre"]:
        st.session_state["ovb_ref_pers_nombre"] = datos["ref_pers_nombre"]
    if "ref_pers_tel_fijo" in datos and datos["ref_pers_tel_fijo"]:
        st.session_state["ovb_ref_pers_tel_fijo"] = datos["ref_pers_tel_fijo"]
    if "ref_pers_celular" in datos and datos["ref_pers_celular"]:
        st.session_state["ovb_ref_pers_celular"] = datos["ref_pers_celular"]
    if "ref_pers_dir" in datos and datos["ref_pers_dir"]:
        st.session_state["ovb_ref_pers_dir"] = datos["ref_pers_dir"]
    if "ref_pers_ciudad" in datos and datos["ref_pers_ciudad"]:
        code = datos["ref_pers_ciudad"]
        st.session_state["ovb_ref_pers_ciudad"] = DANE_TO_MUNICIPIO.get(code, code)
    if "ref_fam_nombre" in datos and datos["ref_fam_nombre"]:
        st.session_state["ovb_ref_fam_nombre"] = datos["ref_fam_nombre"]
    if "ref_fam_tel_fijo" in datos and datos["ref_fam_tel_fijo"]:
        st.session_state["ovb_ref_fam_tel_fijo"] = datos["ref_fam_tel_fijo"]
    if "ref_fam_celular" in datos and datos["ref_fam_celular"]:
        st.session_state["ovb_ref_fam_celular"] = datos["ref_fam_celular"]
    if "ref_fam_dir" in datos and datos["ref_fam_dir"]:
        st.session_state["ovb_ref_fam_dir"] = datos["ref_fam_dir"]
    if "ref_fam_ciudad" in datos and datos["ref_fam_ciudad"]:
        code = datos["ref_fam_ciudad"]
        st.session_state["ovb_ref_fam_ciudad"] = DANE_TO_MUNICIPIO.get(code, code)


def render_ovb_module():
    """Renderiza la interfaz del Módulo OVB: Vinculación del Cliente."""
    st.markdown(
        '<div class="module-tag">OVB &bull; Vinculación del Cliente</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Vinculación del Cliente")
    st.caption(
        "Datos de nacimiento, expedición de documento, residencia, ocupación, "
        "información fiscal y referencias para la inyección en SIIF."
    )

    render_insolvency_banner()
    if session_active() and not st.session_state.get("ovb_auto_cargado"):
        st.session_state["ovb_auto_cargado"] = True
        if not insolvency_blocks():
            try:
                response = execute_process("OVB", action="read")
                datos = (response.data or {}).get("fields") or {}
                if response.ok and any(datos.values()):
                    populate_ovb_from_siif(datos)
            except Exception:
                pass


    # ── Inicializar session_state ─────────────────────────────────────────────
    defaults = {
        "ovb_ciudad_nacimiento":    _MUNICIPIOS_LIST[0],
        "ovb_tipo_nacionalidad":    "1",
        "ovb_pais_expedicion":      "CO",
        "ovb_ciudad_expedicion":    _MUNICIPIOS_LIST[0],
        "ovb_fecha_expedicion":     date.today(),
        "ovb_genero":               "1",
        "ovb_pais_domicilio":       "CO",
        "ovb_ciudad_residencia":    _MUNICIPIOS_LIST[0],
        "ovb_direccion_residencia": "",
        "ovb_barrio":               "",
        "ovb_celular":              "",
        "ovb_profesion":            "",
        "ovb_correo":               "",
        "ovb_nombre_empresa":       "",
        "ovb_dir_empresa":          "",
        "ovb_tel_empresa":          "",
        "ovb_ciudad_empresa":       _MUNICIPIOS_LIST[0],
        "ovb_detalle_actividad":    _ACT_LIST[0],
        "ovb_cargo":                _CARGO_LIST[0],
        "ovb_declara_renta":        "2",
        "ovb_contabilidad":         "2",
        "ovb_dir_reporte":          "2",
        "ovb_origen_fondos":        "",
        "ovb_ref_pers_nombre":      "",
        "ovb_ref_pers_tel_fijo":    "",
        "ovb_ref_pers_celular":     "",
        "ovb_ref_pers_dir":         "",
        "ovb_ref_pers_ciudad":      _MUNICIPIOS_LIST[0],
        "ovb_ref_fam_nombre":       "",
        "ovb_ref_fam_tel_fijo":     "",
        "ovb_ref_fam_celular":      "",
        "ovb_ref_fam_dir":          "",
        "ovb_ref_fam_ciudad":       _MUNICIPIOS_LIST[0],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    with st.form("form_ovb_vinculacion", clear_on_submit=False):

        # ── Bloque 1: Nacimiento ──────────────────────────────────────────────
        st.markdown("#### Datos de Nacimiento")
        col_cn, col_tn = st.columns(2)

        with col_cn:
            ciudad_nacimiento = st.selectbox(
                "Ciudad de Nacimiento",
                options=_MUNICIPIOS_LIST,
                index=_idx(_MUNICIPIOS_LIST, st.session_state.get("ovb_ciudad_nacimiento", _MUNICIPIOS_LIST[0])),
                key="ovb_sel_ciudad_nac",
                help="SIIF N0001 — se inyecta el código DANE del municipio",
            )

        with col_tn:
            tipo_nac = st.selectbox(
                "Tipo de Nacionalidad",
                options=_NAC_LIST,
                index=_idx(_NAC_LIST, st.session_state.get("ovb_tipo_nacionalidad", "1")),
                format_func=lambda k: TIPO_NACIONALIDAD_OPTS[k],
                key="ovb_sel_tipo_nac",
                help="SIIF N0002: 1 = NACIONAL · 2 = EXTRANJERO",
            )

        st.markdown("---")
        # ── Bloque 2: Expedición del Documento ───────────────────────────────
        st.markdown("#### Expedición del Documento")
        col_pe, col_ce, col_fe = st.columns(3)

        with col_pe:
            pais_expedicion = st.selectbox(
                "País de Expedición",
                options=_PAIS_LIST,
                index=0,
                format_func=lambda k: PAIS_OPTS[k],
                key="ovb_sel_pais_exp",
                help="SIIF N0005: CO = Colombia",
            )

        with col_ce:
            ciudad_expedicion = st.selectbox(
                "Ciudad de Expedición",
                options=_MUNICIPIOS_LIST,
                index=_idx(_MUNICIPIOS_LIST, st.session_state.get("ovb_ciudad_expedicion", _MUNICIPIOS_LIST[0])),
                key="ovb_sel_ciudad_exp",
                help="SIIF N0006 — se inyecta el código DANE",
            )

        with col_fe:
            fecha_expedicion = st.date_input(
                "Fecha de Expedición del ID",
                value=st.session_state.get("ovb_fecha_expedicion", date.today()),
                max_value=date.today(),
                key="ovb_fecha_exp",
                help="SIIF N0008 — se envía en formato AAAAMMDD",
                format="DD/MM/YYYY",
            )

        st.markdown("---")
        # ── Bloque 3: Género ──────────────────────────────────────────────────
        st.markdown("#### Género")
        col_gen, _spc = st.columns([1, 2])
        with col_gen:
            genero = st.selectbox(
                "Género",
                options=_GENERO_LIST,
                index=_idx(_GENERO_LIST, st.session_state.get("ovb_genero", "1")),
                format_func=lambda k: GENERO_OPTS[k],
                key="ovb_sel_genero",
                help="SIIF N0009: 1=MASCULINO · 2=FEMENINO · 3=NO BINARIO · 4=TRANS",
            )

        st.markdown("---")
        # ── Bloque 4: Domicilio y Residencia ──────────────────────────────────
        st.markdown("#### Domicilio y Residencia")
        col_pd, col_cr = st.columns(2)

        with col_pd:
            pais_domicilio = st.selectbox(
                "País de Domicilio",
                options=_PAIS_LIST,
                index=0,
                format_func=lambda k: PAIS_OPTS[k],
                key="ovb_sel_pais_dom",
                help="SIIF N0010: CO = Colombia",
            )

        with col_cr:
            ciudad_residencia = st.selectbox(
                "Ciudad de Residencia",
                options=_MUNICIPIOS_LIST,
                index=_idx(_MUNICIPIOS_LIST, st.session_state.get("ovb_ciudad_residencia", _MUNICIPIOS_LIST[0])),
                key="ovb_sel_ciudad_res",
                help="SIIF N0011 — se inyecta el código DANE",
            )

        col_dir, col_barrio = st.columns(2)
        with col_dir:
            direccion_residencia = st.text_input(
                "Dirección de Residencia",
                value=st.session_state.get("ovb_direccion_residencia", ""),
                placeholder="Ej: Cra 15 # 45-32 Apto 201",
                key="ovb_inp_dir",
                help="Campo N0012 del SIIF",
            )
        with col_barrio:
            barrio = st.text_input(
                "Barrio",
                value=st.session_state.get("ovb_barrio", ""),
                placeholder="Ej: El Poblado",
                key="ovb_inp_barrio",
                help="Campo N0013 del SIIF",
            )

        st.markdown("---")
        # ── Bloque 5: Contacto ────────────────────────────────────────────────
        st.markdown("#### Contacto")
        col_cel, _spc2 = st.columns([1, 2])
        with col_cel:
            celular = st.text_input(
                "Celular del Cliente",
                value=st.session_state.get("ovb_celular", ""),
                placeholder="Ej: 3001234567",
                max_chars=10,
                key="ovb_inp_celular",
                help="Campo N0015 del SIIF",
            )

        st.markdown("---")
        # ── Bloque 6: Información Personal y Profesional ─────────────────────
        st.markdown("#### Información Personal y Profesional")
        col_prof, col_correo = st.columns(2)
        with col_prof:
            profesion = st.text_input(
                "Profesión",
                value=st.session_state.get("ovb_profesion", ""),
                placeholder="Ej: Comerciante, Ingeniero...",
                key="ovb_inp_profesion",
                help="Campo N0018 del SIIF",
            )
        with col_correo:
            correo = st.text_input(
                "Correo Electrónico",
                value=st.session_state.get("ovb_correo", ""),
                placeholder="Ej: cliente@email.com",
                key="ovb_inp_correo",
                help="Campo N0020 del SIIF",
            )

        st.markdown("---")
        # ── Bloque 7: Información Laboral ─────────────────────────────────────
        st.markdown("#### Información Laboral")
        col_emp1, col_emp2 = st.columns(2)
        with col_emp1:
            nombre_empresa = st.text_input(
                "Nombre de la Empresa",
                value=st.session_state.get("ovb_nombre_empresa", ""),
                placeholder="Ej: Comercio El Éxito S.A.S.",
                key="ovb_inp_nombre_emp",
                help="Campo N0023 del SIIF",
            )
        with col_emp2:
            dir_empresa = st.text_input(
                "Dirección de la Empresa",
                value=st.session_state.get("ovb_dir_empresa", ""),
                placeholder="Ej: Cra 10 # 20-30 Local 5",
                key="ovb_inp_dir_emp",
                help="Campo N0024 del SIIF",
            )
        col_emp3, col_emp4 = st.columns(2)
        with col_emp3:
            tel_empresa = st.text_input(
                "Teléfono de la Empresa",
                value=st.session_state.get("ovb_tel_empresa", ""),
                placeholder="Ej: 6024521030",
                key="ovb_inp_tel_emp",
                help="Campo N0025 del SIIF",
            )
        with col_emp4:
            ciudad_empresa = st.selectbox(
                "Ciudad de la Empresa",
                options=_MUNICIPIOS_LIST,
                index=_idx(_MUNICIPIOS_LIST, st.session_state.get("ovb_ciudad_empresa", _MUNICIPIOS_LIST[0])),
                key="ovb_sel_ciudad_emp",
                help="SIIF N0026 — se inyecta el código DANE",
            )
        col_act, col_cargo = st.columns(2)
        with col_act:
            detalle_actividad = st.selectbox(
                "Detalle Actividad Económica",
                options=_ACT_LIST,
                index=_idx(_ACT_LIST, st.session_state.get("ovb_detalle_actividad", _ACT_LIST[0])),
                format_func=lambda k: DETALLE_ACTIVIDAD_OPTS[k],
                key="ovb_sel_det_act",
                help="SIIF N0027 — se inyecta el número (1=AGROPECUARIO … 7=SERVICIOS)",
            )
        with col_cargo:
            cargo = st.selectbox(
                "Cargo",
                options=_CARGO_LIST,
                index=_idx(_CARGO_LIST, st.session_state.get("ovb_cargo", _CARGO_LIST[0])),
                format_func=lambda k: CARGO_OPTS[k],
                key="ovb_sel_cargo",
                help="SIIF N0028 — se inyecta el número",
            )

        st.markdown("---")
        # ── Bloque 8: Información Fiscal ──────────────────────────────────────
        st.markdown("#### Información Fiscal")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            declara_renta = st.selectbox(
                "¿Declara Renta?",
                options=_SINO_LIST,
                index=_idx(_SINO_LIST, st.session_state.get("ovb_declara_renta", "2")),
                format_func=lambda k: SI_NO_SIIF_OPTS[k],
                key="ovb_sel_declara_renta",
                help="SIIF N0044: 1 = SÍ · 2 = NO",
            )
        with col_r2:
            contabilidad = st.selectbox(
                "¿Lleva Contabilidad?",
                options=_SINO_LIST,
                index=_idx(_SINO_LIST, st.session_state.get("ovb_contabilidad", "2")),
                format_func=lambda k: SI_NO_SIIF_OPTS[k],
                key="ovb_sel_contabilidad",
                help="SIIF N0045: 1 = SÍ · 2 = NO",
            )
        with col_r3:
            dir_reporte = st.selectbox(
                "¿Dir. Reporte Anual de Costos?",
                options=_SINO_LIST,
                index=_idx(_SINO_LIST, st.session_state.get("ovb_dir_reporte", "2")),
                format_func=lambda k: SI_NO_SIIF_OPTS[k],
                key="ovb_sel_dir_reporte",
                help="SIIF N0046: 1 = SÍ · 2 = NO",
            )

        st.markdown("---")
        # ── Bloque 9: Origen de los Fondos ────────────────────────────────────
        st.markdown("#### Origen de los Fondos")
        origen_fondos = st.text_area(
            "Justificación del Origen de los Fondos",
            value=st.session_state.get("ovb_origen_fondos", ""),
            placeholder="Ej: Recursos provenientes de actividad comercial independiente...",
            height=100,
            key="ovb_inp_origen_fondos",
            help="Campo texW0050 del SIIF — también se usará como Resultado de Entrevista (texW0074)",
        )

        st.markdown("---")
        # ── Bloque 10: Referencia Personal ───────────────────────────────────
        st.markdown("#### Referencia Personal")
        col_rp1, col_rp2 = st.columns(2)
        with col_rp1:
            ref_pers_nombre = st.text_input(
                "Nombre Completo",
                value=st.session_state.get("ovb_ref_pers_nombre", ""),
                placeholder="Ej: María Pérez López",
                key="ovb_inp_rp_nombre",
                help="Campo N0051 del SIIF",
            )
        with col_rp2:
            ref_pers_tel_fijo = st.text_input(
                "Teléfono Fijo",
                value=st.session_state.get("ovb_ref_pers_tel_fijo", ""),
                placeholder="Ej: 6024568900",
                key="ovb_inp_rp_tel",
                help="Campo N0052 del SIIF",
            )
        col_rp3, col_rp4 = st.columns(2)
        with col_rp3:
            ref_pers_celular = st.text_input(
                "Celular",
                value=st.session_state.get("ovb_ref_pers_celular", ""),
                placeholder="Ej: 3209876543",
                key="ovb_inp_rp_cel",
                help="Campo N0053 del SIIF",
            )
        with col_rp4:
            ref_pers_dir = st.text_input(
                "Dirección",
                value=st.session_state.get("ovb_ref_pers_dir", ""),
                placeholder="Ej: Cra 25 # 10-15",
                key="ovb_inp_rp_dir",
                help="Campo N0054 del SIIF",
            )
        col_rp5, _rp_spc = st.columns([1, 1])
        with col_rp5:
            ref_pers_ciudad = st.selectbox(
                "Ciudad (Ref. Personal)",
                options=_MUNICIPIOS_LIST,
                index=_idx(_MUNICIPIOS_LIST, st.session_state.get("ovb_ref_pers_ciudad", _MUNICIPIOS_LIST[0])),
                key="ovb_sel_rp_ciudad",
                help="SIIF N0055 — se inyecta el código DANE",
            )

        st.markdown("---")
        # ── Bloque 11: Referencia Familiar ───────────────────────────────────
        st.markdown("#### Referencia Familiar")
        col_rf1, col_rf2 = st.columns(2)
        with col_rf1:
            ref_fam_nombre = st.text_input(
                "Nombre Completo",
                value=st.session_state.get("ovb_ref_fam_nombre", ""),
                placeholder="Ej: Carlos García Ruiz",
                key="ovb_inp_rf_nombre",
                help="Campo N0061 del SIIF",
            )
        with col_rf2:
            ref_fam_tel_fijo = st.text_input(
                "Teléfono Fijo",
                value=st.session_state.get("ovb_ref_fam_tel_fijo", ""),
                placeholder="Ej: 6024511200",
                key="ovb_inp_rf_tel",
                help="Campo N0062 del SIIF",
            )
        col_rf3, col_rf4 = st.columns(2)
        with col_rf3:
            ref_fam_celular = st.text_input(
                "Celular",
                value=st.session_state.get("ovb_ref_fam_celular", ""),
                placeholder="Ej: 3155432100",
                key="ovb_inp_rf_cel",
                help="Campo N0063 del SIIF",
            )
        with col_rf4:
            ref_fam_dir = st.text_input(
                "Dirección",
                value=st.session_state.get("ovb_ref_fam_dir", ""),
                placeholder="Ej: Calle 8 # 5-40",
                key="ovb_inp_rf_dir",
                help="Campo N0064 del SIIF",
            )
        col_rf5, _rf_spc = st.columns([1, 1])
        with col_rf5:
            ref_fam_ciudad = st.selectbox(
                "Ciudad (Ref. Familiar)",
                options=_MUNICIPIOS_LIST,
                index=_idx(_MUNICIPIOS_LIST, st.session_state.get("ovb_ref_fam_ciudad", _MUNICIPIOS_LIST[0])),
                key="ovb_sel_rf_ciudad",
                help="SIIF N0065 — se inyecta el código DANE",
            )

        st.markdown("---")
        col_izq, col_centro, col_der = st.columns([1.2, 1, 1.2])
        with col_centro:
            btn_enviar = st.form_submit_button(
                "Enviar",
                width='stretch',
                type="primary",
            )

    # ── Procesamiento al enviar ───────────────────────────────────────────────
    if btn_enviar:
        if not direccion_residencia.strip():
            st.error("La Dirección de Residencia es obligatoria.")
            return
        if not celular.strip() or not celular.strip().isdigit():
            st.error("Ingrese un número de celular válido (sólo dígitos).")
            return

        # Persistir en session_state
        st.session_state["ovb_ciudad_nacimiento"]    = ciudad_nacimiento
        st.session_state["ovb_tipo_nacionalidad"]    = tipo_nac
        st.session_state["ovb_pais_expedicion"]      = pais_expedicion
        st.session_state["ovb_ciudad_expedicion"]    = ciudad_expedicion
        st.session_state["ovb_fecha_expedicion"]     = fecha_expedicion
        st.session_state["ovb_genero"]               = genero
        st.session_state["ovb_pais_domicilio"]       = pais_domicilio
        st.session_state["ovb_ciudad_residencia"]    = ciudad_residencia
        st.session_state["ovb_direccion_residencia"] = direccion_residencia.strip()
        st.session_state["ovb_barrio"]               = barrio.strip()
        st.session_state["ovb_celular"]              = celular.strip()
        st.session_state["ovb_profesion"]            = profesion.strip()
        st.session_state["ovb_correo"]               = correo.strip()
        st.session_state["ovb_nombre_empresa"]       = nombre_empresa.strip()
        st.session_state["ovb_dir_empresa"]          = dir_empresa.strip()
        st.session_state["ovb_tel_empresa"]          = tel_empresa.strip()
        st.session_state["ovb_ciudad_empresa"]       = ciudad_empresa
        st.session_state["ovb_detalle_actividad"]    = detalle_actividad
        st.session_state["ovb_cargo"]                = cargo
        st.session_state["ovb_declara_renta"]        = declara_renta
        st.session_state["ovb_contabilidad"]         = contabilidad
        st.session_state["ovb_dir_reporte"]          = dir_reporte
        st.session_state["ovb_origen_fondos"]        = origen_fondos.strip()
        st.session_state["ovb_ref_pers_nombre"]      = ref_pers_nombre.strip()
        st.session_state["ovb_ref_pers_tel_fijo"]    = ref_pers_tel_fijo.strip()
        st.session_state["ovb_ref_pers_celular"]     = ref_pers_celular.strip()
        st.session_state["ovb_ref_pers_dir"]         = ref_pers_dir.strip()
        st.session_state["ovb_ref_pers_ciudad"]      = ref_pers_ciudad
        st.session_state["ovb_ref_fam_nombre"]       = ref_fam_nombre.strip()
        st.session_state["ovb_ref_fam_tel_fijo"]     = ref_fam_tel_fijo.strip()
        st.session_state["ovb_ref_fam_celular"]      = ref_fam_celular.strip()
        st.session_state["ovb_ref_fam_dir"]          = ref_fam_dir.strip()
        st.session_state["ovb_ref_fam_ciudad"]       = ref_fam_ciudad
        st.session_state["ovb_registrado"]           = True

        # Payload con valores SIIF listos para el subproceso OVB
        st.session_state["ovb_payload"] = {
            "ciudad_nacimiento":     MUNICIPIOS_DANE.get(ciudad_nacimiento, ciudad_nacimiento),
            "tipo_nacionalidad":     tipo_nac,
            "pais_expedicion":       pais_expedicion,
            "ciudad_expedicion":     MUNICIPIOS_DANE.get(ciudad_expedicion, ciudad_expedicion),
            "fecha_expedicion":      fecha_expedicion.strftime("%Y%m%d"),
            "genero":                genero,
            "pais_domicilio":        pais_domicilio,
            "ciudad_residencia":     MUNICIPIOS_DANE.get(ciudad_residencia, ciudad_residencia),
            "direccion_residencia":  direccion_residencia.strip(),
            "barrio":                barrio.strip(),
            "celular":               celular.strip(),
            "profesion":             profesion.strip(),
            "envio_correspondencia": "1",
            "correo":                correo.strip(),
            "como_se_entero":        "1",
            "nombre_empresa":        nombre_empresa.strip(),
            "dir_empresa":           dir_empresa.strip(),
            "tel_empresa":           tel_empresa.strip(),
            "ciudad_empresa":        MUNICIPIOS_DANE.get(ciudad_empresa, ciudad_empresa),
            "detalle_actividad":     detalle_actividad,
            "cargo":                 cargo,
            "trans_moneda_ext":      "2",
            "seleccione_opcion":     "2",
            "declara_renta":         declara_renta,
            "contabilidad":          contabilidad,
            "dir_reporte":           dir_reporte,
            "origen_fondos":         origen_fondos.strip(),
            "ref_pers_nombre":       ref_pers_nombre.strip(),
            "ref_pers_tel_fijo":     ref_pers_tel_fijo.strip(),
            "ref_pers_celular":      ref_pers_celular.strip(),
            "ref_pers_dir":          ref_pers_dir.strip(),
            "ref_pers_ciudad":       MUNICIPIOS_DANE.get(ref_pers_ciudad, ref_pers_ciudad),
            "ref_fam_nombre":        ref_fam_nombre.strip(),
            "ref_fam_tel_fijo":      ref_fam_tel_fijo.strip(),
            "ref_fam_celular":       ref_fam_celular.strip(),
            "ref_fam_dir":           ref_fam_dir.strip(),
            "ref_fam_ciudad":        MUNICIPIOS_DANE.get(ref_fam_ciudad, ref_fam_ciudad),
            "resultado_entrevista":  origen_fondos.strip(),
        }

        solicitud_id = st.session_state.get("solicitud_id", "N/A")
        if insolvency_blocks():
            st.error("Envío bloqueado: el cliente consultado está en insolvencia.")
        elif not session_active():
            st.info("Inicie sesión SIIF. El payload OVB quedó guardado localmente.")
        else:
            with st.spinner("El Bot inyecta la vinculación en SIIF (OVB)..."):
                try:
                    response = execute_process("OVB", **st.session_state["ovb_payload"])
                except BotClientError as exc:
                    st.error(str(exc))
                    response = None
            if response is not None and response.ok:
                st.success(response.message)
            elif response is not None:
                st.error(response.message)

    # ── Tarjeta de resumen ────────────────────────────────────────────────────
    if st.session_state.get("ovb_registrado"):
        payload  = st.session_state.get("ovb_payload", {})
        c_nac    = st.session_state.get("ovb_ciudad_nacimiento", "")
        c_exp    = st.session_state.get("ovb_ciudad_expedicion", "")
        c_res    = st.session_state.get("ovb_ciudad_residencia", "")
        c_emp    = st.session_state.get("ovb_ciudad_empresa", "")
        c_rp     = st.session_state.get("ovb_ref_pers_ciudad", "")
        c_rf     = st.session_state.get("ovb_ref_fam_ciudad", "")
        nac_lbl  = TIPO_NACIONALIDAD_OPTS.get(payload.get("tipo_nacionalidad", "1"), "")
        gen_lbl  = GENERO_OPTS.get(payload.get("genero", "1"), "")
        act_lbl  = DETALLE_ACTIVIDAD_OPTS.get(payload.get("detalle_actividad", "1"), "")
        car_lbl  = CARGO_OPTS.get(payload.get("cargo", "1"), "")
        dr_lbl   = SI_NO_SIIF_OPTS.get(payload.get("declara_renta", "2"), "")
        con_lbl  = SI_NO_SIIF_OPTS.get(payload.get("contabilidad", "2"), "")
        rep_lbl  = SI_NO_SIIF_OPTS.get(payload.get("dir_reporte", "2"), "")

        st.markdown("---")
        st.markdown(
            f"""
            <div class="result-card">
                <h4>Ficha de Vinculación (OVB)</h4>
                <p>
                    <strong>Nacimiento:</strong> {c_nac} <code>{payload.get('ciudad_nacimiento', '')}</code>
                    &nbsp;|&nbsp; <strong>Nacionalidad:</strong> {nac_lbl}
                    &nbsp;|&nbsp; <strong>Género:</strong> {gen_lbl}
                </p>
                <p>
                    <strong>Expedición Doc.:</strong>
                    País <code>{payload.get('pais_expedicion', '')}</code> &mdash;
                    {c_exp} <code>{payload.get('ciudad_expedicion', '')}</code> &mdash;
                    Fecha: <code>{payload.get('fecha_expedicion', '')}</code>
                </p>
                <p>
                    <strong>Residencia:</strong>
                    {c_res} <code>{payload.get('ciudad_residencia', '')}</code> &mdash;
                    {payload.get('direccion_residencia', '')} — Barrio: {payload.get('barrio', '')}
                    &nbsp;|&nbsp; <strong>Cel:</strong> {payload.get('celular', '')}
                </p>
                <p>
                    <strong>Profesión:</strong> {payload.get('profesion', '')}
                    &nbsp;|&nbsp; <strong>Correo:</strong> {payload.get('correo', '')}
                </p>
                <p>
                    <strong>Empresa:</strong> {payload.get('nombre_empresa', '')} &mdash;
                    {c_emp} <code>{payload.get('ciudad_empresa', '')}</code> &mdash;
                    Tel: {payload.get('tel_empresa', '')}
                </p>
                <p>
                    <strong>Actividad:</strong> {act_lbl} <code>{payload.get('detalle_actividad', '')}</code>
                    &nbsp;|&nbsp; <strong>Cargo:</strong> {car_lbl} <code>{payload.get('cargo', '')}</code>
                </p>
                <p>
                    <strong>Declara Renta:</strong> {dr_lbl}
                    &nbsp;|&nbsp; <strong>Contabilidad:</strong> {con_lbl}
                    &nbsp;|&nbsp; <strong>Dir. Reporte Costos:</strong> {rep_lbl}
                </p>
                <p>
                    <strong>Origen Fondos:</strong> {payload.get('origen_fondos', '')}
                </p>
                <p>
                    <strong>Ref. Personal:</strong> {payload.get('ref_pers_nombre', '')} &mdash;
                    {c_rp} <code>{payload.get('ref_pers_ciudad', '')}</code>
                </p>
                <p>
                    <strong>Ref. Familiar:</strong> {payload.get('ref_fam_nombre', '')} &mdash;
                    {c_rf} <code>{payload.get('ref_fam_ciudad', '')}</code>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
