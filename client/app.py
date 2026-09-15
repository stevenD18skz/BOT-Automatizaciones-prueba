"""UI del Bot SIIF (Streamlit), con la interfaz de credioro-app.

El login se hace en la barra lateral y todo viaja por el WebSocket hacia el
proceso del Bot. Esta UI nunca toca Selenium.

Lo único funcional es la Consulta de Cuentas de Ahorros (login, consulta, lote,
demo y monitor en vivo). Los módulos de CrediOro (`client/credioro/`) son una
maqueta visual: se ven igual que en credioro-app pero no están conectados.

Ejecutar con:  streamlit run client/app.py
(o `python main.py`, que levanta Bot + UI de una sola vez)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

import protocol  # noqa: E402
from client.credioro.modules.aut import render_aut_module  # noqa: E402
from client.credioro.modules.cliente import render_cliente_module  # noqa: E402
from client.credioro.modules.garantia import render_garantia_module  # noqa: E402
from client.credioro.modules.monitor import render_proceso_monitor_module  # noqa: E402
from client.credioro.modules.oif import render_oif_module  # noqa: E402
from client.credioro.modules.orc import render_orc_module  # noqa: E402
from client.credioro.modules.ova import render_ova_module  # noqa: E402
from client.credioro.modules.ovb import render_ovb_module  # noqa: E402
from client.credioro.modules.simulador import _kpi_html, render_simulador_module  # noqa: E402
from client.credioro.modules.validaciones import render_validaciones_module  # noqa: E402
from client.credioro.styles import inject_styles  # noqa: E402
from client.ipc import BotClient, BotClientError, ensure_bot_running, is_bot_running  # noqa: E402
from config.settings import BOT_HOST, BOT_PORT, BOT_NAME, PROCESS_NAME  # noqa: E402
from services.data.cuentas import limpiar_cuentas  # noqa: E402

st.set_page_config(
    page_title="Bot SIIF - Banco Unión",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

LEVEL_ICONS = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}
LOGO_PATH = Path(__file__).resolve().parent / "credioro" / "assets" / "bancounion.svg"

# Estado que esperan los módulos de CrediOro (mismos valores por defecto que allá)
_DEFAULTS_CREDIORO = {
    "username_siif": "",
    "siif_session_active": False,
    "sim_num_doc_val": "",
    "sim_gramos_val": 0.0,
    "sim_valor_financiacion": "",
    "sim_intereses": "",
    "sim_cuota_admon": "",
    "sim_cuota_total": "",
    "sim_confirme_valor": "",
    "sim_credioros_vigentes": "—",
    "sim_saldo_pendiente": "—",
    "cliente_bloqueado_insolvencia": False,
    "cliente_nombre_insolvencia": "",
    "solicitud_id": None,
    "org_camera_enabled": False,
    "oif_completado": False,
    "orc_decision": "—",
    "orc_valor_credito": "—",
    "orc_completado": False,
    "ova_completado": False,
    "aut_completado": False,
    "cliente_registrado": False,
}
for _key, _value in _DEFAULTS_CREDIORO.items():
    st.session_state.setdefault(_key, _value)


@st.cache_resource
def get_client() -> BotClient:
    """Un solo cliente para toda la app; sobrevive a los reruns de Streamlit."""
    ensure_bot_running()
    client = BotClient()
    client.start()
    return client


client = get_client()
st.session_state.setdefault("last_seq", 0)
st.session_state.setdefault("rendered_logged_in", None)
st.session_state.setdefault("rendered_connected", client.connected)

state = client.snapshot()
# Los módulos de CrediOro miran estas llaves para decidir qué avisos mostrar
st.session_state["siif_session_active"] = bool(client.connected and state.get("logged_in"))
if state.get("username"):
    st.session_state["username_siif"] = state["username"]


def run_command(cmd: str, payload: dict | None = None) -> protocol.Response | None:
    try:
        return client.send(cmd, payload)
    except BotClientError as exc:
        st.error(str(exc))
        return None


def cuentas_desde_texto(texto: str) -> list[str] | None:
    """Revisa las cuentas antes de enviarlas, para avisar sin esperar al Bot."""
    validas, invalidas = limpiar_cuentas(texto)
    if invalidas:
        st.warning("Solo se admiten dígitos. Revisa: " + ", ".join(invalidas[:5]))
        return None
    if not validas:
        st.warning("Escribe al menos un número de cuenta.")
        return None
    return validas


def logo_html() -> str:
    try:
        svg = LOGO_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""
    svg = svg.replace('fill="#00A3E1"', 'fill="#19BCE0"')
    return svg.replace('width="82"', 'width="130"').replace('height="32"', 'height="50"')


def espacio() -> None:
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


# --- barra lateral ----------------------------------------------------------
with st.sidebar:
    st.markdown(
        f'<div class="sidebar-logo-wrap">{logo_html()}'
        '<div class="sidebar-app-name">Bot SIIF</div>'
        '<div class="sidebar-app-sub">Automatizaciones &mdash; Banco Unión</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-section-lbl">Credenciales SIIF</div>', unsafe_allow_html=True)

    # El formulario de login queda fuera del fragmento: con el refresco de 1 s
    # los campos se redibujarían mientras escribes.
    sesion_abierta = st.session_state["siif_session_active"]
    if not sesion_abierta and not state.get("connecting"):
        username = st.text_input("Usuario SIIF", placeholder="Ingresa tu usuario", key="inp_username_siif")
        password = st.text_input("Contraseña SIIF", type="password", placeholder="Contraseña", key="inp_password_siif")
        if st.button("Iniciar Sesión SIIF", width="stretch", type="primary", key="btn_login_siif"):
            if not is_bot_running():
                st.error("El Bot no está corriendo. Levántalo más abajo.")
            elif not username.strip() or not password:
                st.warning("Ingresa usuario y contraseña de SIIF.")
            else:
                response = run_command(
                    protocol.CMD_LOGIN, {"username": username.strip(), "password": password}
                )
                if response and response.ok:
                    st.rerun()
                elif response:
                    st.error(response.message)

    @st.fragment(run_every="1s")
    def panel_conexion() -> None:
        """Estado vivo del Bot y de la sesión; sin esto se quedaría congelado."""
        conectado = client.connected
        snap = client.snapshot()

        if not conectado:
            st.error(f"Bot no disponible · ws://{BOT_HOST}:{BOT_PORT}")
            if st.button("Levantar el Bot", width="stretch", key="btn_levantar_bot"):
                with st.spinner("Arrancando el proceso del Bot..."):
                    ensure_bot_running()
        elif snap.get("connecting"):
            st.info("El Bot está autenticando en SIIF...")
        elif snap.get("logged_in"):
            st.success(f"Sesión SIIF activa ({snap.get('username', '')})")
            if st.button("Cerrar sesión SIIF", width="stretch", key="btn_logout_siif"):
                run_command(protocol.CMD_LOGOUT)
                st.rerun(scope="app")
        else:
            st.info("Bot listo · sin sesión SIIF")

        # Al caerse o volver el Bot cambia también el cuerpo, y eso pide un rerun
        # completo. El flag se actualiza ANTES de pedirlo: si no, se cicla.
        if conectado != st.session_state.rendered_connected:
            st.session_state.rendered_connected = conectado
            st.rerun(scope="app")

    panel_conexion()

    st.markdown('<div class="sidebar-section-lbl">Arquitectura</div>', unsafe_allow_html=True)
    st.caption(
        "Streamlit es solo el cliente. Selenium vive en el proceso Bot "
        f"(`{BOT_HOST}:{BOT_PORT}`) para no bloquear la interfaz."
    )
    st.caption(f"{BOT_NAME} · {PROCESS_NAME}")


# --- encabezado -------------------------------------------------------------
st.markdown(
    "<div>"
    '<h1 style="font-size:1.65rem;color:#1A2B3C;margin:0 0 4px;font-family:Inter,sans-serif;font-weight:700;">'
    "Proceso CrediOro"
    "</h1>"
    '<p style="font-size:.88rem;color:#7A94A8;margin:0 0 16px;font-family:Inter,sans-serif;">'
    "Cliente local. El Bot Selenium autentica y ejecuta SIIF en un proceso aparte. "
    "Por ahora solo la Consulta de Cuentas de Ahorros está conectada; el resto es maqueta visual."
    "</p>"
    "</div>",
    unsafe_allow_html=True,
)

_PASOS = [
    ("modulo-cuentas", "★", "Cuentas de Ahorros"),
    ("modulo-sim", "0", "Simulador"),
    ("modulo-1", "1", "Cliente"),
    ("modulo-2", "2", "Validaciones"),
    ("modulo-oif", "3", "OIF"),
    ("modulo-orc", "4", "ORC"),
    ("modulo-ovb", "5", "OVB"),
    ("modulo-aut", "6", "AUT"),
    ("modulo-org", "7", "Garantías"),
    ("modulo-ova", "8", "OVA"),
    ("modulo-bot", "42", "Monitor"),
]
st.markdown(
    '<div class="linear-flow-banner">'
    + '<span style="color:#C8D8E4;">&rsaquo;</span>'.join(
        f'<a href="#{ancla}" class="linear-step-item"><span class="linear-step-num">{num}</span> {nombre}</a>'
        for ancla, num, nombre in _PASOS
    )
    + "</div>",
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown('<div class="module-tag">Autenticación &bull; SIIF</div>', unsafe_allow_html=True)
    st.markdown("### Estado de la sesión")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Bot", "En línea" if client.connected else "Fuera de línea")
    if not client.connected:
        estado_sesion = "—"
    elif state.get("connecting"):
        estado_sesion = "Conectando"
    elif state.get("logged_in"):
        estado_sesion = "Activa"
    else:
        estado_sesion = "Sin sesión"
    col_b.metric("Sesión", estado_sesion)
    col_c.metric("Usuario", state.get("username") or "—")
    if not st.session_state["siif_session_active"]:
        st.info("Inicie sesión SIIF en la barra lateral para habilitar la consulta.")
espacio()


# --- Consulta de Cuentas de Ahorros (lo único conectado al Bot) --------------
# Usa los mismos componentes visuales que los módulos de CrediOro: tarjetas de
# sección, KPIs del simulador y la tarjeta de decisión del ORC.
def seccion(titulo: str, etiqueta: str) -> None:
    st.markdown(
        f'<div class="sim-section-card"><div class="sim-section-title">{titulo}'
        f'<span class="sim-badge-tag">{etiqueta}</span></div></div>',
        unsafe_allow_html=True,
    )


def tarjeta_estado(tipo: str, icono: str, etiqueta: str, titulo: str, detalle: str, pie: str = "") -> None:
    """Tarjeta tipo decisión del ORC. `tipo`: aprobado, rechazado o pendiente."""
    st.markdown(
        f'<div class="decision-card decision-card-{tipo}">'
        f'<div class="decision-icon-wrapper decision-icon-{tipo}">{icono}</div>'
        '<div class="decision-content">'
        '<div class="decision-header-row">'
        '<span class="decision-title-tag">Cuentas de Ahorros</span>'
        f'<span class="decision-badge decision-badge-{tipo}">{etiqueta}</span>'
        "</div>"
        f'<div class="decision-main-text decision-text-{tipo}">{titulo}</div>'
        f'<div class="decision-subtext">{detalle}</div>'
        + (f'<div class="decision-footer-info">{pie}</div>' if pie else "")
        + "</div></div>",
        unsafe_allow_html=True,
    )


def boton_centrado(etiqueta: str, **kwargs) -> bool:
    _, centro, _ = st.columns([1.2, 1, 1.2])
    with centro:
        return st.button(etiqueta, width="stretch", **kwargs)


def render_cuentas_module() -> None:
    st.markdown('<div class="module-tag">Módulo &#9733; &bull; Cuentas de Ahorros</div>', unsafe_allow_html=True)
    st.markdown("### Consulta de Cuentas de Ahorros")
    st.caption(
        "El Bot navega SIIF, consulta cada cuenta y devuelve el resultado en vivo. "
        "Puede consultar cuentas sueltas o correr el lote de ENTRADAS.xlsx."
    )
    st.markdown("---")

    st.session_state.rendered_logged_in = state.get("logged_in", False)

    if not client.connected:
        # Sin conexión el estado que tenemos es el último conocido, no el real.
        tarjeta_estado(
            "rechazado", "&#10005;", "Fuera de línea", "Bot no disponible",
            "Levántelo desde la barra lateral o con <code>python -m bot.server</code>; "
            "la interfaz se reconecta sola.",
        )
        return

    if state.get("connecting"):
        tarjeta_estado(
            "pendiente", "&#8635;", "Autenticando", "Iniciando sesión en SIIF",
            "El Bot está abriendo Chrome e ingresando sus credenciales. Puede tardar unos segundos.",
        )

        @st.fragment(run_every="0.5s")
        def esperar_login() -> None:
            if not client.snapshot().get("connecting"):
                st.rerun(scope="app")

        esperar_login()
        return

    if not state.get("logged_in") and not state.get("running"):
        render_demo()
        return

    if state.get("logged_in"):
        # Fuera del fragmento a propósito: con el refresco cada 0.5 s el cuadro de
        # texto se redibujaría mientras escribes.
        seccion("Cuentas a Consultar", "Consulta Individual")
        texto_cuentas = st.text_area(
            "Números de cuenta",
            placeholder="Uno por línea, o separados por comas",
            height=90,
            key="cuentas_texto",
        )
        if boton_centrado("Consultar cuentas", type="primary", key="btn_cuentas_consultar"):
            cuentas = cuentas_desde_texto(texto_cuentas)
            if cuentas:
                response = run_command(protocol.CMD_CONSULTAR, {"cuentas": cuentas})
                if response and response.ok:
                    st.toast(response.message, icon="🔎")
                elif response:
                    st.error(response.message)
        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

    live_panel()


def render_demo() -> None:
    if state.get("last_message"):
        st.error(state["last_message"])
    tarjeta_estado(
        "pendiente", "&#128274;", "Sin sesión", "Inicie sesión SIIF",
        "Ingrese sus credenciales en la barra lateral para consultar cuentas reales.",
    )

    seccion("Modo Demo", "Sin SIIF")
    st.caption(
        "La demo recorre un lote falso emitiendo los mismos eventos que una corrida "
        "real, sin abrir Chrome ni tocar SIIF."
    )
    cuentas_demo = st.text_area(
        "Cuentas a simular (opcional)",
        placeholder="Si escribe cuentas, la demo simula consultarlas a ellas en vez de generar registros",
        height=80,
    )
    col_reg, col_pausa = st.columns(2)
    registros = col_reg.number_input("Registros", 3, 100, 12)
    pausa = col_pausa.number_input("Segundos por registro", 0.2, 5.0, 1.0, step=0.1)
    if boton_centrado("Lanzar demo", type="primary", key="btn_cuentas_demo"):
        payload: dict = {"registros": int(registros), "pausa": float(pausa)}
        cuentas = cuentas_desde_texto(cuentas_demo) if cuentas_demo.strip() else []
        if cuentas is not None:
            if cuentas:
                payload["cuentas"] = cuentas
            response = run_command(protocol.CMD_DEMO, payload)
            if response and response.ok:
                st.rerun()
            elif response:
                st.error(response.message)


@st.fragment(run_every="0.5s")
def live_panel() -> None:
    """Se refresca solo cada 0.5s con lo que el Bot vaya empujando.

    Los botones viven aquí dentro y no en el cuerpo: si no, se quedarían
    habilitados o deshabilitados según el estado del último dibujado.
    """
    snap = client.snapshot()

    if snap.get("logged_in") is False and st.session_state.rendered_logged_in:
        st.rerun(scope="app")

    running = snap.get("running", False)

    if not snap.get("logged_in"):
        tarjeta_estado(
            "pendiente", "&#127916;", "Modo demo", "Datos simulados",
            "No se está tocando SIIF: los registros son falsos.",
        )
        if boton_centrado("← Volver", disabled=running, key="btn_cuentas_volver"):
            st.rerun(scope="app")
    else:
        seccion("Procesamiento por Lote", "ENTRADAS.xlsx")
        _, col_run, col_stop, _ = st.columns([0.6, 1.2, 1, 0.6])
        if col_run.button(
            "Ejecutar lote", type="primary", disabled=running, width="stretch", key="btn_cuentas_lote"
        ):
            response = run_command(protocol.CMD_EXECUTE)
            if response and response.ok:
                st.toast("Proceso iniciado", icon="▶️")
            elif response:
                st.error(response.message)
        if col_stop.button("Detener", disabled=not running, width="stretch", key="btn_cuentas_detener"):
            run_command(protocol.CMD_STOP)
            st.toast("Detención solicitada", icon="⏹️")

    progress = snap.get("progress") or {}
    counters = snap.get("counters") or {}
    current = progress.get("current", 0)
    total = progress.get("total", 0)

    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
    seccion("Progreso de la Consulta", "En vivo" if running else "En espera")
    st.markdown(
        '<div class="sim-grid">'
        + _kpi_html("Total", str(total))
        + _kpi_html("Procesados", str(current), highlight=True)
        + _kpi_html("Éxitos", str(counters.get("exitos", 0)))
        + _kpi_html("Errores", str(counters.get("errores", 0)))
        + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
    if total:
        label = f"Cuenta {progress.get('numero_cuenta', '')}" if running else "En espera"
        st.progress(min(current / total, 1.0), text=f"{current}/{total} — {label}")
    else:
        st.progress(0.0, text="Sin proceso ejecutado todavía")

    # Toasts solo para lo que llegó desde el último refresco
    events = client.recent_events(limit=60)
    seq = client.event_seq
    if seq > st.session_state.last_seq:
        nuevos = seq - st.session_state.last_seq
        for event in events[-nuevos:]:
            if event.event == protocol.EVT_RUN_FINISHED:
                resumen = event.payload
                st.toast(
                    f"Proceso terminado — {resumen.get('exitos', 0)} éxitos, "
                    f"{resumen.get('errores', 0)} errores",
                    icon="🏁",
                )
            elif event.event == protocol.EVT_RECORD and not event.payload.get("ok"):
                st.toast(f"Error en cuenta {event.payload.get('numero_cuenta', '')}", icon="⚠️")
        st.session_state.last_seq = seq

    summary = snap.get("last_summary")
    if summary and not running:
        que = "consulta" if summary.get("origen") == "ui" else "corrida"
        resumen = (
            f"{summary.get('exitos', 0)} éxitos, {summary.get('errores', 0)} errores "
            f"de {summary.get('total', 0)} registros"
        )
        pie = ""
        if summary.get("trazabilidad"):
            pie = (
                f'<span class="decision-status-pill">Trazabilidad {summary.get("run_id", "")}</span>'
                f'<span>{summary["trazabilidad"]}</span>'
            )
        if summary.get("error"):
            tarjeta_estado(
                "rechazado", "&#10005;", "Interrumpida", f"Última {que} interrumpida",
                f"{summary['error']} — {resumen}.", pie,
            )
        elif summary.get("detenido"):
            tarjeta_estado(
                "pendiente", "&#10074;&#10074;", "Detenida", f"Última {que} detenida",
                f"Detenida por el usuario — {resumen}.", pie,
            )
        else:
            tipo = "rechazado" if summary.get("errores") and not summary.get("exitos") else "aprobado"
            tarjeta_estado(
                tipo, "&#10003;", "Completada", f"Última {que} completada", f"{resumen}.", pie,
            )

    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
    seccion("Resultados", "Registros procesados")
    tab_resultados, tab_log = st.tabs(["Resultados", "Actividad del Bot"])

    with tab_resultados:
        records = client.all_records()
        if records:
            st.dataframe(records, width="stretch", hide_index=True)
        else:
            st.caption("Aún no hay registros procesados.")

    with tab_log:
        lines = []
        for event in reversed(events):
            if event.event == protocol.EVT_LOG:
                icon = LEVEL_ICONS.get(event.payload.get("level", "info"), "ℹ️")
                lines.append(f"{icon} {event.payload.get('message', '')}")
            elif event.event == protocol.EVT_RECORD:
                icon = "✅" if event.payload.get("ok") else "❌"
                lines.append(
                    f"{icon} {event.payload.get('numero_cuenta', '')} → "
                    f"{event.payload.get('message', '')}"
                )
        st.code("\n".join(lines) or "Sin actividad todavía", language=None)


st.markdown('<div id="modulo-cuentas"></div>', unsafe_allow_html=True)
with st.container(border=True):
    render_cuentas_module()
espacio()


# --- módulos de CrediOro (maqueta visual, sin conexión) ----------------------
_MODULOS_CREDIORO = [
    ("modulo-sim", render_simulador_module),
    ("modulo-1", render_cliente_module),
    ("modulo-2", render_validaciones_module),
    ("modulo-oif", render_oif_module),
    ("modulo-orc", render_orc_module),
    ("modulo-ovb", render_ovb_module),
    ("modulo-aut", render_aut_module),
    ("modulo-org", render_garantia_module),
    ("modulo-ova", render_ova_module),
    ("modulo-bot", render_proceso_monitor_module),
]
for ancla, render in _MODULOS_CREDIORO:
    st.markdown(f'<div id="{ancla}"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        render()
    espacio()

st.markdown(
    '<div class="footer-bar">'
    "Banco Unión S.A. &nbsp;&middot;&nbsp; Bot SIIF "
    "&nbsp;&middot;&nbsp; Bot independiente &nbsp;&middot;&nbsp; &copy; 2026"
    "</div>",
    unsafe_allow_html=True,
)
