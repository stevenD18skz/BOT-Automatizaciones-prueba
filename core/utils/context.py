import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import WebDriverWait

from core.constants import DEFAULT_ELEMENT_TIMEOUT


class FrameContext:
    """
    Context manager para entrar/salir de un <iframe> de forma segura.

    - Espera hasta que el frame esté disponible y hace switch.
    - Al salir, regresa al contenido principal.
    """

    def __init__(self, driver: WebDriver, frame_name: str, timeout: int | None = None):
        self.driver = driver
        self.frame_name = frame_name
        # Usar timeout específico de búsqueda si no se provee
        self.timeout = timeout or DEFAULT_ELEMENT_TIMEOUT

    def __enter__(self):
        try:
            logging.debug(f"Esperando frame '{self.frame_name}' hasta {self.timeout}s")
            WebDriverWait(self.driver, self.timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.NAME, self.frame_name))
            )
            logging.debug(f"Frame '{self.frame_name}' disponible y activo.")
        except Exception as e:
            logging.warning(f"No se pudo acceder al frame '{self.frame_name}': {e}")
            # Intentar switch directo como fallback
            try:
                self.driver.switch_to.frame(self.frame_name)
                logging.debug(
                    f"Fallback: switch_to.frame('{self.frame_name}') exitoso."
                )
            except Exception as inner:
                logging.error(f"Falló fallback de frame '{self.frame_name}': {inner}")
                raise
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.driver.switch_to.default_content()
            logging.debug("Regresando al contenido principal.")
        except Exception as e:
            logging.error(f"Error al salir del frame '{self.frame_name}': {e}")
            raise
