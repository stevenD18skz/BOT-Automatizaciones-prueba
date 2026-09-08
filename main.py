import logging

from config.settings import BOT_NAME, PROCESS_NAME
from core.utils.logging import setup_logging
from services.workflows.orchestrator import Orchestrator


def main():
    f"""
    Punto de entrada para el proceso de {PROCESS_NAME}.
    Configura logging, ejecuta la orquestación y maneja excepciones globales.
    """
    try:
        setup_logging()
        logging.info(f"=== Iniciando proceso RPA {BOT_NAME} ===")
        orchestrator = Orchestrator()
        orchestrator.run()
    except KeyboardInterrupt:
        logging.info("=== Proceso RPA interrumpido por el usuario ===")
    except SystemExit:
        logging.info("=== Proceso RPA terminado por el usuario ===")
    except Exception as e:
        logging.error(f"Error en el proceso RPA: {e}")
        raise
    finally:
        logging.info("=== Proceso RPA finalizado ===")


if __name__ == "__main__":
    main()
