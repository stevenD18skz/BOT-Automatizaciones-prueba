"""Simulador CrediOro: el Bot captura el valor de la solicitud en SIIF."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from client.credioro.bot_ops import BotClient, BotClientError, ensure_bot_running
from client.credioro.form_options import (
    SI_NO_OPTS,
    TIPO_DOC_SIMULADOR_OPTS,
    TIPO_ORO_SIMULADOR_OPTS,
)
from client.credioro.bot_ops import InsolvencyService
from client.credioro.bot_ops import STATUS_BLOCKED


def _fmt_cop(valor: str) -> str:
    try:
        num = float(str(valor).replace(",", ".").replace("$", "").strip())
        return f"$ {num:,.0f}"
    except (ValueError, AttributeError):
        return valor or "—"


def _kpi_html(label: str, value: str, highlight: bool = False) -> str:
    cls = "sim-kpi-item sim-kpi-item-highlight" if highlight else "sim-kpi-item"
    val_cls = "sim-kpi-val-main" if highlight else "sim-kpi-val"
    return (
        f'<div class="{cls}">'
        f'  <div class="sim-kpi-label">{label}</div>'
        f'  <div class="{val_cls}">{value}</div>'
        f"</div>"
    )


def _bot_client() -> BotClient:
    if "bot_client" not in st.session_state:
        st.session_state["bot_client"] = BotClient()
    return st.session_state["bot_client"]


def _render_insolvencia(num_doc: str) -> bool:
    doc_limpio = InsolvencyService.clean_document(num_doc)
    if not doc_limpio:
        st.caption(
            "Ingrese el documento para cruzarlo con la base de insolvencia "
            "(src/data/insolvency/)."
        )
        st.session_state["cliente_bloqueado_insolvencia"] = False
        st.session_state["cliente_nombre_insolvencia"] = ""
        return False

    res = InsolvencyService.lookup_by_document(num_doc)
    st.session_state["insolvencia_info"] = res
    st.session_state["sim_num_doc_val"] = doc_limpio

    if not res.get("base_disponible"):
        st.warning(res.get("mensaje") or "Base de insolvencia no disponible.")
        st.session_state["cliente_bloqueado_insolvencia"] = False
        st.session_state["cliente_nombre_insolvencia"] = ""
        return False

    if res.get("es_insolvente"):
        st.session_state["cliente_bloqueado_insolvencia"] = True
        st.session_state["cliente_nombre_insolvencia"] = res.get("nombre_cliente", "")
        st.session_state["sim_nombre_cliente"] = res.get("nombre_cliente", "")
        archivo = Path(res.get("archivo_origen") or "").name or "ENTRADAS.xlsx"
        st.markdown(
            f"""
            <div class="insolvencia-card-blocked">
                <div class="insolvencia-header-row">
                    <span class="insolvencia-badge-blocked">
                        PROCESO BLOQUEADO &bull; CLIENTE EN INSOLVENCIA
                    </span>
                    <span style="font-size:0.75rem;color:#BE123C;font-weight:700;">Base: {archivo}</span>
                </div>
                <div class="insolvencia-title-blocked">
                    {res.get('nombre_cliente') or 'Cliente reportado'}
                </div>
                <div class="insolvencia-detail-grid">
                    <div class="insolvencia-detail-item">
                        <span class="insolvencia-detail-lbl">Identificación</span>
                        <span class="insolvencia-detail-val">{res.get('identificacion')}</span>
                    </div>
                    <div class="insolvencia-detail-item">
                        <span class="insolvencia-detail-lbl">Obligaciones</span>
                        <span class="insolvencia-detail-val">{res.get('total_obligaciones')}</span>
                    </div>
                    <div class="insolvencia-detail-item">
                        <span class="insolvencia-detail-lbl">Saldo capital</span>
                        <span class="insolvencia-detail-val" style="color:#BE123C;">{res.get('saldo_capital_total_fmt')}</span>
                    </div>
                    <div class="insolvencia-detail-item">
                        <span class="insolvencia-detail-lbl">Fecha trámite</span>
                        <span class="insolvencia-detail-val">{res.get('fecha_tramite') or 'Registrado en base'}</span>
                    </div>
                </div>
                <div class="insolvencia-notice">
                    <strong>RESTRICCIÓN:</strong> Ley 1564. No se permite simular ni desembolsar CrediOro.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return True

    st.session_state["cliente_bloqueado_insolvencia"] = False
    st.session_state["cliente_nombre_insolvencia"] = ""
    archivo = Path(res.get("archivo_origen") or "").name or "ENTRADAS.xlsx"
    st.markdown(
        f"""
        <div class="insolvencia-card-ok">
            <span class="insolvencia-badge-ok">HABILITADO</span>
            <span style="font-size:0.85rem;color:#065F46;font-weight:600;">
                Identificación <strong>{doc_limpio}</strong> verificada en <em>{archivo}</em>
                — sin trámite de insolvencia.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return False


def render_simulador_module() -> None:
    st.markdown(
        '<div class="module-tag">Simulador &bull; SIIF CrediOro</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Simulador de Crédito CrediOro")
    st.caption(
        "El Bot navega SIIF, captura el valor de financiación y lo confirma solo. "
        "La interfaz no pide el valor de la solicitud."
    )
    st.markdown("---")

    st.markdown(
        '<div class="sim-section-card"><div class="sim-section-title">'
        "Datos de Identificación del Cliente"
        '<span class="sim-badge-tag">Información Básica</span>'
        "</div></div>",
        unsafe_allow_html=True,
    )
    col_tipo, col_num = st.columns([1, 2])
    with col_tipo:
        tipo_doc_key = st.selectbox(
            "Tipo de Identificación",
            options=list(TIPO_DOC_SIMULADOR_OPTS.keys()),
            format_func=lambda k: TIPO_DOC_SIMULADOR_OPTS[k],
            key="sim_tipo_doc",
        )
    with col_num:
        num_doc = st.text_input(
            "Número de Documento",
            value=st.session_state.get("sim_num_doc_val", ""),
            placeholder="Ej: 1020304050",
            key="sim_num_doc",
        )

    bloqueado = _render_insolvencia(num_doc)
    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

    cred_vigentes = st.session_state.get("sim_credioros_vigentes", "—")
    saldo_pend = st.session_state.get("sim_saldo_pendiente", "—")
    st.markdown(
        '<div class="sim-section-card"><div class="sim-section-title">'
        "Historial de Credioros Vigentes"
        '<span class="sim-badge-tag">Capturado por el Bot</span>'
        "</div></div>",
        unsafe_allow_html=True,
    )
    col_vig, col_saldo = st.columns(2)
    with col_vig:
        st.markdown(_kpi_html("Credioros Vigentes", str(cred_vigentes or "—")), unsafe_allow_html=True)
    with col_saldo:
        saldo_fmt = _fmt_cop(str(saldo_pend)) if saldo_pend not in ("—", "", None) else "—"
        st.markdown(_kpi_html("Saldo Pendiente de Pago", saldo_fmt), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="sim-section-card"><div class="sim-section-title">'
        "Configuración de la Garantía"
        '<span class="sim-badge-tag">Tipo de Oro</span>'
        "</div></div>",
        unsafe_allow_html=True,
    )
    col_oro, col_grs = st.columns([2, 1])
    with col_oro:
        tipo_oro = st.selectbox("Tipo de Oro", options=TIPO_ORO_SIMULADOR_OPTS, key="sim_tipo_oro")
    with col_grs:
        gramos = st.number_input(
            "Gramos a Liquidar",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            value=float(st.session_state.get("sim_gramos_val", 0.0)),
            key="sim_gramos",
        )
    col_reloj, col_blanco = st.columns(2)
    with col_reloj:
        reloj = st.selectbox(
            "¿Es un Reloj?",
            options=list(SI_NO_OPTS.keys()),
            format_func=lambda k: SI_NO_OPTS[k],
            index=1,
            key="sim_reloj",
        )
    with col_blanco:
        oro_blanco = st.selectbox(
            "¿Es Oro Blanco?",
            options=list(SI_NO_OPTS.keys()),
            format_func=lambda k: SI_NO_OPTS[k],
            index=1,
            key="sim_oro_blanco",
        )

    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="sim-section-card"><div class="sim-section-title">'
        "Resultados de Simulación"
        '<span class="sim-badge-tag">Capturado por Selenium</span>'
        "</div></div>",
        unsafe_allow_html=True,
    )
    st.caption("El Bot lee R006 y confirma ese mismo valor en SIIF. No hay campo editable de solicitud.")

    val_financiacion = st.session_state.get("sim_valor_financiacion", "")
    val_intereses = st.session_state.get("sim_intereses", "")
    val_admon = st.session_state.get("sim_cuota_admon", "")
    val_cuota_total = st.session_state.get("sim_cuota_total", "")
    val_confirme = st.session_state.get("sim_confirme_valor", "")

    st.markdown(
        '<div class="sim-grid">'
        + _kpi_html("Valor de la solicitud", _fmt_cop(val_confirme or val_financiacion), highlight=True)
        + _kpi_html("Valor de Financiación", _fmt_cop(val_financiacion), highlight=True)
        + _kpi_html("Intereses Aprox. c/Estudio", _fmt_cop(val_intereses))
        + _kpi_html("Cuota Admón. Aprox. c/Estudio", _fmt_cop(val_admon))
        + _kpi_html("Cuota Total Aprox. c/Estudio", _fmt_cop(val_cuota_total), highlight=True)
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    sesion_ok = st.session_state.get("siif_session_active", False)
    col_izq, col_centro, col_der = st.columns([1.2, 1, 1.2])
    with col_centro:
        enviar = st.button(
            "Enviar al Bot",
            key="btn_simulador_enviar",
            width='stretch',
            type="primary",
        )

    if bloqueado:
        st.error("Proceso restringido: el cliente está en trámite de insolvencia.")
    elif not sesion_ok:
        st.info("Inicie sesión SIIF en la barra lateral antes de simular.")

    if enviar:
        errores = []
        if bloqueado:
            errores.append("Cliente reportado en insolvencia.")
        if not sesion_ok:
            errores.append("No hay sesión SIIF activa.")
        if not num_doc.strip():
            errores.append("Número de documento es requerido.")
        if gramos <= 0:
            errores.append("Los gramos a liquidar deben ser mayores a 0.")
        if errores:
            for err in errores:
                st.error(err)
            return

        payload = {
            "tipo_doc_value": tipo_doc_key,
            "num_doc": num_doc.strip(),
            "plazo_inicial": "06",
            "tipo_oro": tipo_oro,
            "gramos": gramos,
            "reloj": reloj,
            "oro_blanco": oro_blanco,
        }
        st.session_state["sim_payload"] = payload
        st.session_state["sim_gramos_val"] = gramos
        with st.spinner("El Bot está simulando en SIIF y capturando el valor de la solicitud..."):
            try:
                client = ensure_bot_running(_bot_client())
                response = client.simulate(payload)
            except BotClientError as exc:
                st.error(str(exc))
                return

        data = response.data or {}
        if response.ok:
            st.session_state["sim_valor_financiacion"] = data.get("valor_financiacion", "")
            st.session_state["sim_intereses"] = data.get("intereses", "")
            st.session_state["sim_cuota_admon"] = data.get("cuota_admon", "")
            st.session_state["sim_cuota_total"] = data.get("cuota_total", "")
            st.session_state["sim_confirme_valor"] = data.get("confirme_valor", "")
            st.session_state["sim_credioros_vigentes"] = data.get("credioros_vigentes", "—")
            st.session_state["sim_saldo_pendiente"] = data.get("saldo_pendiente", "—")
            st.session_state["solicitud_id"] = data.get("solicitud_id")
            st.success(
                "Simulación completada. Valor de solicitud capturado: "
                f"{_fmt_cop(st.session_state['sim_confirme_valor'] or st.session_state['sim_valor_financiacion'])}."
            )
            st.rerun()
        else:
            if data.get("insolvencia", {}).get("es_insolvente") or response.status == STATUS_BLOCKED:
                st.session_state["cliente_bloqueado_insolvencia"] = True
            st.error(response.message)
