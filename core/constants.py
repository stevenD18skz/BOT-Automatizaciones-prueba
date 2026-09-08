"""
Constantes del Framework RPA Core

Este módulo centraliza todas las constantes utilizadas por el framework
para facilitar el mantenimiento y configuración.
"""

# Timeouts login
DEFAULT_LOGIN_TIMEOUT = 300

# Timeouts por defecto (en segundos)
DEFAULT_TIMEOUT = 30
DEFAULT_ELEMENT_TIMEOUT = 10
DEFAULT_PAGE_LOAD_TIMEOUT = 30
DEFAULT_AJAX_TIMEOUT = 15

# Intervalos de verificación (en segundos)
DEFAULT_POLL_FREQUENCY = 0.5
DEFAULT_RETRY_INTERVAL = 1.0

# Configuración de reintentos
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 2.0

# Configuración de logging
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(module)s] %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configuración de archivos
DEFAULT_LOG_FILE = "logs/rpa.log"
DEFAULT_LOG_MAX_SIZE = 5 * 1024 * 1024  # 5MB
DEFAULT_LOG_BACKUP_COUNT = 5

# Localizadores comunes reutilizables
COMMON_SELECTORS = {
    "search_inputs": [
        ("name", "q"),
        ("name", "search"),
        ("id", "search"),
        ("id", "query"),
        ("xpath", "//input[@type='search']"),
        ("xpath", "//input[@placeholder*='search' or @placeholder*='Search']"),
    ],
    "submit_buttons": [
        ("xpath", "//input[@type='submit']"),
        ("xpath", "//button[@type='submit']"),
        ("xpath", "//button[contains(text(), 'Submit')]"),
        ("xpath", "//button[contains(text(), 'Send')]"),
        ("xpath", "//button[contains(text(), 'Search')]"),
        ("xpath", "//input[@value='Submit']"),
    ],
    "login_buttons": [
        ("xpath", "//button[contains(text(), 'Login')]"),
        ("xpath", "//button[contains(text(), 'Sign In')]"),
        ("xpath", "//input[@type='submit']"),
        ("id", "login"),
        ("id", "signin"),
        ("class name", "login-button"),
    ],
    "error_indicators": [
        ("xpath", "//*[contains(text(), 'Error')]"),
        ("xpath", "//*[contains(text(), '404')]"),
        ("xpath", "//*[contains(text(), '500')]"),
        ("xpath", "//*[contains(text(), 'Not Found')]"),
        ("class name", "error"),
        ("class name", "alert-error"),
        ("class name", "alert-danger"),
    ],
    "success_indicators": [
        ("xpath", "//*[contains(text(), 'Success')]"),
        ("xpath", "//*[contains(text(), 'Successful')]"),
        ("xpath", "//*[contains(text(), 'Complete')]"),
        ("class name", "success"),
        ("class name", "alert-success"),
        ("class name", "success-message"),
    ],
    "loading_indicators": [
        ("xpath", "//*[contains(text(), 'Loading')]"),
        ("xpath", "//*[contains(text(), 'Please wait')]"),
        ("class name", "loading"),
        ("class name", "spinner"),
        ("class name", "loader"),
    ],
}

# Mensajes estándar
MESSAGES = {
    "validation": {
        "missing_params": "Parámetros faltantes: {params}",
        "empty_params": "Parámetros vacíos: {params}",
        "invalid_url": "URL inválida: {url}",
        "invalid_email": "Email inválido: {email}",
    },
    "navigation": {
        "success": "Navegación exitosa a {url}",
        "failed": "Falló navegación a {url}",
        "timeout": "Timeout navegando a {url} después de {timeout}s",
    },
    "elements": {
        "not_found": "Elemento no encontrado: {locator}",
        "not_clickable": "Elemento no clickeable: {locator}",
        "not_visible": "Elemento no visible: {locator}",
        "found": "Elemento encontrado: {locator}",
    },
    "process": {
        "start": "Iniciando proceso {name} con parámetros: {params}",
        "success": "Proceso {name} completado exitosamente",
        "failed": "Proceso {name} falló: {error}",
        "retry": "Reintentando {action}, intento {attempt} de {max_attempts}",
    },
}

# Configuraciones específicas del navegador
BROWSER_CONFIG = {
    "chrome": {
        "options": [
            # "--headless=new",
            "--disable-blink-features=AutomationControlled",  # Evita detección de automatización
            "--disable-extensions",  # Evita interferencias de extensiones
            "--no-sandbox",  # Necesario para algunos entornos
            "--disable-dev-shm-usage",  # Evita problemas de memoria
            "--disable-gpu",  # Evita problemas de renderizado
            "--start-maximized",  # Maximiza la ventana para mejor interacción
            "--disable-web-security",  # Evita bloqueos de CORS si es necesario
            "--user-data-dir=/tmp/chrome_dev_test",  # Directorio temporal para evitar conflictos
        ],
        "prefs": {
            "profile.default_content_setting_values.notifications": 2,  # Bloquea notificaciones
            "profile.managed_default_content_settings.images": 1,  # Mantén imágenes habilitadas para SIIF
            "profile.default_content_settings.popups": 0,  # Bloquea popups
        },
    },
    "firefox": {
        "options": [
            "--headless" if False else "",
        ],
        "prefs": {
            "dom.webnotifications.enabled": False,
            "media.volume_scale": "0.0",
        },
    },
}

# Patrones regex útiles
REGEX_PATTERNS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "url": r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
    "phone": r"^[\+]?[1-9][\d]{0,15}$",
    "date_iso": r"^\d{4}-\d{2}-\d{2}$",
    "time_24h": r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
}

# Estados del proceso
PROCESS_STATUS = {
    "PENDING": "pendiente",
    "RUNNING": "ejecutando",
    "SUCCESS": "exitoso",
    "FAILED": "fallido",
    "TIMEOUT": "timeout",
    "CANCELLED": "cancelado",
}
