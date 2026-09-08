"""Lanzador: arranca el Bot (WebSocket) y la UI (Streamlit) con un solo comando.

    python main.py

El Bot abre su propia ventana de consola para que veas el flujo de eventos en
vivo; Streamlit se queda en esta terminal y el navegador se abre solo.

Si prefieres arrancarlos por separado (útil para depurar):
    python -m bot.server
    streamlit run client/app.py
"""

import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from client.ipc import ensure_bot_running, is_bot_running
from config.settings import BOT_HOST, BOT_PORT, UI_PORT

BASE_DIR = Path(__file__).resolve().parent
UI_URL = f"http://{BOT_HOST}:{UI_PORT}"


def _port_open(port: int) -> bool:
    try:
        with socket.create_connection((BOT_HOST, port), timeout=0.5):
            return True
    except OSError:
        return False


def _open_browser_when_ready() -> None:
    for _ in range(60):
        if _port_open(UI_PORT):
            webbrowser.open(UI_URL)
            return
        time.sleep(0.5)


def main() -> None:
    print("=" * 60)
    print("  Bot SIIF — arrancando Bot + UI")
    print("=" * 60)

    if is_bot_running():
        print(f"  Bot ya estaba corriendo en ws://{BOT_HOST}:{BOT_PORT}")
    else:
        print("  Levantando el Bot (se abrirá otra ventana de consola)...")
        if not ensure_bot_running():
            print("  ERROR: el Bot no respondió. Revisa la ventana del Bot.")
            sys.exit(1)
        print(f"  Bot escuchando en ws://{BOT_HOST}:{BOT_PORT}")

    print(f"  Abriendo la interfaz en {UI_URL} ...\n")
    threading.Thread(target=_open_browser_when_ready, daemon=True).start()

    try:
        # headless: evita que Streamlit pida un email por consola en el primer arranque.
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(BASE_DIR / "client" / "app.py"),
                "--server.headless=true",
                f"--server.port={UI_PORT}",
            ],
            cwd=str(BASE_DIR),
            check=False,
        )
    except KeyboardInterrupt:
        pass
    finally:
        print("\n  UI cerrada. El Bot sigue corriendo en su ventana; ciérrala con Ctrl+C.")


if __name__ == "__main__":
    main()
