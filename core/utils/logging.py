import logging
import sys
import os
import warnings
from logging.handlers import RotatingFileHandler
from pathlib import Path
import io


def setup_logging(log_file: str = "logs/rpa.log"):
    """
    Configura el logging con:
      - Formato con timestamp, nivel y módulo.
      - Handler a consola para INFO+.
      - Handler de archivo rotativo para DEBUG+.
      - Captura excepciones no manejadas (incluye KeyboardInterrupt).
      - Suprime logs externos (TensorFlow, Selenium, etc.)
    """
    # Suprimir logs externos ANTES de configurar el logging
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # TensorFlow
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # TensorFlow optimizations
    warnings.filterwarnings("ignore")  # Warnings de Python

    # Suprimir stderr de Chrome/WebDriver temporalmente
    class StderrFilter:
        def __init__(self):
            self.original_stderr = sys.stderr
            self.filtered_stderr = io.StringIO()

        def __enter__(self):
            sys.stderr = self.filtered_stderr
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stderr = self.original_stderr

    # Asegurar existencia del directorio de logs
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Logger raíz
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Limpiar handlers existentes
    logger.handlers.clear()

    # Formato común
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(module)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Filtro para excluir logs externos
    class ExternalLibraryFilter(logging.Filter):
        def filter(self, record):
            # Lista de mensajes que no queremos mostrar
            unwanted_messages = [
                "DevTools listening",
                "Registration response error",
                "TensorFlow",
                "DEPRECATED_ENDPOINT",
                "Created TensorFlow",
                "Attempting to use a delegate",
                "WARNING: All log messages",
                "Registering VoiceTranscriptionCapability",
                "webdriver_manager",
                "WDM",
                "Get LATEST chromedriver",
            ]
            message = record.getMessage()
            return not any(msg in message for msg in unwanted_messages)

    # Handler de consola (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ExternalLibraryFilter())
    logger.addHandler(console_handler)

    # Handler de archivo rotativo (sin filtro para tener logs completos en archivo)
    file_handler = RotatingFileHandler(
        filename=str(log_path),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Suprimir logs específicos de librerías externas
    logging.getLogger("selenium").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    # websockets en DEBUG escribe cada keepalive y ahoga el log del proceso.
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("webdriver_manager").setLevel(logging.ERROR)
    logging.getLogger("WDM").setLevel(logging.ERROR)
    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(
        logging.ERROR
    )

    # Suprimir logs de Chrome/TensorFlow que no pasan por logging
    for logger_name in ["absl", "tensorflow", "google"]:
        logging.getLogger(logger_name).setLevel(logging.ERROR)

    # Capturar excepciones no manejadas
    def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            logger.warning("Proceso interrumpido por teclado (KeyboardInterrupt)")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.error(
            "Excepción no capturada", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_unhandled_exception
