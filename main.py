"""Lanzador: arranca el Bot (WebSocket) y la UI (Streamlit) con un solo comando.

    python main.py

El Bot abre su propia ventana de consola para que veas el flujo de eventos en
vivo; Streamlit se queda en esta terminal y abre el navegador solo.

Si prefieres arrancarlos por separado (útil para depurar):
    python -m bot.server
    streamlit run client/app.py
"""

import subprocess
import sys
from pathlib import Path

from client.ipc import ensure_bot_running, is_bot_running
from config.settings import BOT_HOST, BOT_PORT

BASE_DIR = Path(__file__).resolve().parent


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

    print("  Abriendo la interfaz de Streamlit...\n")
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(BASE_DIR / "client" / "app.py")],
            cwd=str(BASE_DIR),
            check=False,
        )
    except KeyboardInterrupt:
        pass
    finally:
        print("\n  UI cerrada. El Bot sigue corriendo en su ventana; ciérrala con Ctrl+C.")


if __name__ == "__main__":
    main()
