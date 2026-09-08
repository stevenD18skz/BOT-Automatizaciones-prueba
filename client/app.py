"""UI del Bot SIIF (Streamlit).

Reemplaza la ventana de Tkinter: el login se hace acá y todo lo demás viaja por
el WebSocket hacia el proceso del Bot. Esta UI nunca toca Selenium.

Ejecutar con:  streamlit run client/app.py
(o `python main.py`, que levanta Bot + UI de una sola vez)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

import protocol  # noqa: E402
from client.ipc import BotClient, BotClientError, ensure_bot_running, is_bot_running  # noqa: E402
from config.settings import BOT_HOST, BOT_PORT, BOT_NAME, PROCESS_NAME  # noqa: E402

st.set_page_config(page_title="Bot SIIF", page_icon="🤖", layout="wide")

LEVEL_ICONS = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}


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


def run_command(cmd: str, payload: dict | None = None) -> protocol.Response | None:
    try:
        return client.send(cmd, payload)
    except BotClientError as exc:
        st.error(str(exc))
        return None


# --- barra lateral ----------------------------------------------------------
# Va en un fragmento porque el cuerpo del script solo se redibuja cuando hay
# interacción: sin esto, el estado de conexión se quedaba congelado y solo se
# enteraba de que el Bot murió (o volvió) al recargar la página a mano.
st.session_state.setdefault("rendered_connected", client.connected)

with st.sidebar:

    @st.fragment(run_every="1s")
    def panel_conexion() -> None:
        conectado = client.connected

        st.subheader("Conexión")
        if conectado:
            st.success(f"Bot conectado\n\nws://{BOT_HOST}:{BOT_PORT}")
        else:
            st.error(f"Sin conexión con el Bot\n\nws://{BOT_HOST}:{BOT_PORT}")
            if st.button("Levantar el Bot", use_container_width=True):
                with st.spinner("Arrancando el proceso del Bot..."):
                    ensure_bot_running()

        state = client.snapshot()
        st.subheader("Sesión SIIF")
        if conectado and state.get("logged_in"):
            st.info(f"Conectado como **{state.get('username', '')}**")
            if st.button("Cerrar sesión SIIF", use_container_width=True):
                run_command(protocol.CMD_LOGOUT)
                st.rerun(scope="app")
        else:
            st.caption("Sin sesión activa")

        st.divider()
        st.caption(f"{BOT_NAME}\n\n{PROCESS_NAME}")

        # Al caerse o volver el Bot cambia también el cuerpo (formulario de login
        # vs panel), y eso pide un rerun completo. El flag se actualiza ANTES de
        # pedirlo: si no, el rerun vuelve a encontrar la diferencia y se cicla.
        if conectado != st.session_state.rendered_connected:
            st.session_state.rendered_connected = conectado
            st.rerun(scope="app")

    panel_conexion()


# --- cuerpo -----------------------------------------------------------------
st.title("🤖 Bot SIIF — Consulta de Cuentas de Ahorros")
state = client.snapshot()
st.session_state.rendered_logged_in = state.get("logged_in", False)

if not client.connected:
    # Sin conexión el estado que tenemos es el último conocido, no el real:
    # mostrar el panel aquí sería mentir sobre una sesión que quizá ya no existe.
    st.warning(
        "El Bot no está disponible. Levántalo desde la barra lateral o con "
        "`python -m bot.server`; la UI se reconecta sola."
    )

elif state.get("connecting"):
    st.info("Abriendo Chrome e iniciando sesión en SIIF... (puede tardar unos segundos)")

    @st.fragment(run_every="0.5s")
    def esperar_login() -> None:
        if not client.snapshot().get("connecting"):
            st.rerun(scope="app")

    esperar_login()

elif not state.get("logged_in") and not state.get("running"):
    if state.get("last_message"):
        st.error(state["last_message"])
    st.markdown(
        "Ingresa tus credenciales de SIIF. El Bot abrirá Chrome y mantendrá la "
        "sesión abierta hasta que cierres sesión."
    )
    with st.form("login"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar sesión", type="primary")

    if submitted:
        if not is_bot_running():
            st.error("El Bot no está corriendo. Usa 'Levantar el Bot' en la barra lateral.")
        elif not username or not password:
            st.warning("Usuario y contraseña son obligatorios")
        else:
            response = run_command(
                protocol.CMD_LOGIN, {"username": username, "password": password}
            )
            if response and response.ok:
                st.rerun()
            elif response:
                st.error(response.message)

    st.divider()
    st.caption(
        "¿Sin credenciales a mano? La demo recorre un lote falso emitiendo los mismos "
        "eventos que una corrida real, sin abrir Chrome ni tocar SIIF."
    )
    demo_cols = st.columns([1, 1, 2])
    registros = demo_cols[0].number_input("Registros", 3, 100, 12)
    pausa = demo_cols[1].number_input("Segundos por registro", 0.2, 5.0, 1.0, step=0.1)
    if demo_cols[2].button("🎬 Lanzar demo", use_container_width=True):
        response = run_command(
            protocol.CMD_DEMO, {"registros": int(registros), "pausa": float(pausa)}
        )
        if response and response.ok:
            st.rerun()
        elif response:
            st.error(response.message)

else:

    @st.fragment(run_every="0.5s")
    def live_panel() -> None:
        """Se refresca solo cada 0.5s con lo que el Bot vaya empujando.

        Los botones viven aquí dentro y no en el cuerpo: si no, se quedarían
        habilitados o deshabilitados según el estado del último dibujado.
        """
        snap = client.snapshot()

        if snap.get("logged_in") is False and st.session_state.rendered_logged_in:
            st.rerun(scope="app")

        if not snap.get("logged_in"):
            aviso, volver = st.columns([3, 1])
            aviso.info("🎬 Modo demo — datos simulados, no se está tocando SIIF.")
            if volver.button(
                "← Volver", use_container_width=True, disabled=snap.get("running")
            ):
                st.rerun(scope="app")

        controls, _ = st.columns([3, 1])
        with controls:
            col_run, col_stop = st.columns(2)
            running = snap.get("running", False)
            if col_run.button(
                "▶ Ejecutar proceso",
                type="primary",
                disabled=running or not snap.get("logged_in"),
                use_container_width=True,
            ):
                response = run_command(protocol.CMD_EXECUTE)
                if response and response.ok:
                    st.toast("Proceso iniciado", icon="▶️")
                elif response:
                    st.error(response.message)

            if col_stop.button(
                "⏹ Detener", disabled=not running, use_container_width=True
            ):
                run_command(protocol.CMD_STOP)
                st.toast("Detención solicitada", icon="⏹️")

        progress = snap.get("progress") or {}
        counters = snap.get("counters") or {}
        current = progress.get("current", 0)
        total = progress.get("total", 0)

        metrics = st.columns(4)
        metrics[0].metric("Total", total)
        metrics[1].metric("Procesados", current)
        metrics[2].metric("Éxitos", counters.get("exitos", 0))
        metrics[3].metric("Errores", counters.get("errores", 0))

        if total:
            share = min(current / total, 1.0)
            label = f"Cuenta {progress.get('numero_cuenta', '')}" if snap.get("running") else "En espera"
            st.progress(share, text=f"{current}/{total} — {label}")
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
                    st.toast(
                        f"Error en cuenta {event.payload.get('numero_cuenta', '')}", icon="⚠️"
                    )
            st.session_state.last_seq = seq

        tab_resultados, tab_log = st.tabs(["Resultados", "Actividad del Bot"])

        with tab_resultados:
            records = client.all_records()
            if records:
                st.dataframe(records, use_container_width=True, hide_index=True)
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

        summary = snap.get("last_summary")
        if summary and not snap.get("running"):
            if summary.get("detenido"):
                st.warning(f"Última corrida detenida: {summary}")
            else:
                st.success(
                    f"Última corrida: {summary.get('exitos', 0)} éxitos, "
                    f"{summary.get('errores', 0)} errores de {summary.get('total', 0)} registros."
                )

    live_panel()
