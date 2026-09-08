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
with st.sidebar:
    st.subheader("Conexión")
    if client.connected:
        st.success(f"Bot conectado\n\nws://{BOT_HOST}:{BOT_PORT}")
    else:
        st.error(f"Sin conexión con el Bot\n\nws://{BOT_HOST}:{BOT_PORT}")
        if st.button("Levantar el Bot", use_container_width=True):
            with st.spinner("Arrancando el proceso del Bot..."):
                if ensure_bot_running():
                    st.toast("Bot levantado", icon="🚀")
                else:
                    st.toast("No se pudo levantar el Bot", icon="❌")
            st.rerun()

    state = client.snapshot()
    st.subheader("Sesión SIIF")
    if state.get("logged_in"):
        st.info(f"Conectado como **{state.get('username', '')}**")
        if st.button("Cerrar sesión SIIF", use_container_width=True):
            run_command(protocol.CMD_LOGOUT)
            st.rerun()
    else:
        st.caption("Sin sesión activa")

    st.divider()
    st.caption(f"{BOT_NAME}\n\n{PROCESS_NAME}")


# --- cuerpo -----------------------------------------------------------------
st.title("🤖 Bot SIIF — Consulta de Cuentas de Ahorros")
state = client.snapshot()
st.session_state.rendered_logged_in = state.get("logged_in", False)

if state.get("connecting"):
    st.info("Abriendo Chrome e iniciando sesión en SIIF... (puede tardar unos segundos)")

    @st.fragment(run_every="0.5s")
    def esperar_login() -> None:
        if not client.snapshot().get("connecting"):
            st.rerun(scope="app")

    esperar_login()

elif not state.get("logged_in"):
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

else:
    controls, _ = st.columns([3, 1])
    with controls:
        col_run, col_stop = st.columns(2)
        running = state.get("running", False)
        if col_run.button(
            "▶ Ejecutar proceso", type="primary", disabled=running, use_container_width=True
        ):
            response = run_command(protocol.CMD_EXECUTE)
            if response and response.ok:
                st.toast("Proceso iniciado", icon="▶️")
            elif response:
                st.error(response.message)
            st.rerun()

        if col_stop.button(
            "⏹ Detener", disabled=not running, use_container_width=True
        ):
            run_command(protocol.CMD_STOP)
            st.toast("Detención solicitada", icon="⏹️")
            st.rerun()

    @st.fragment(run_every="0.5s")
    def live_panel() -> None:
        """Se refresca solo cada 0.5s con lo que el Bot vaya empujando."""
        snap = client.snapshot()

        if snap.get("logged_in") is False and st.session_state.rendered_logged_in:
            st.rerun(scope="app")

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
