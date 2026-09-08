from pathlib import Path

# BOT Name

BOT_NAME = "Bot Plantilla Automatización RPA"
PROCESS_NAME = "Proceso de Consulta de Cuentas de Ahorro"

# SIIF Website
SIIF_URL = "http://siif.girosyfinanzas.com/BUN_V12/"

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Comunicación UI (Streamlit) <-> Bot: WebSocket en localhost.
# 8766 y no 8765 para no chocar con el bot de credioro_app.
BOT_HOST = "127.0.0.1"
BOT_PORT = 8766
BOT_URL = f"ws://{BOT_HOST}:{BOT_PORT}"

# Excel Config
INPUT_FILE_PATH = BASE_DIR / "entradas" / "ENTRADAS.xlsx"
OUTPUT_FILE_PATH = BASE_DIR / "salidas" / "CONCILIACION.xlsx"
ERROR_FILE_PATH = BASE_DIR / "errores" / "ERRORES.xlsx"

# Batch Size
BATCH_SIZE = 100

# Navegation
MENU_ROUTE = {
    "menu": "Sistema de Cuentas de Ahorros",  # Navegación por menús
    "proceso": "CONSULTA DE CUENTAS DE AHORROS",  # Navegación al proceso
}
