import logging

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from core.constants import (
    BROWSER_CONFIG,
    DEFAULT_ELEMENT_TIMEOUT,
    DEFAULT_PAGE_LOAD_TIMEOUT,
)


class ChromeDriver:
    """
    Gestiona el ciclo de vida de las instancias de Chrome WebDriver.

    Esta clase maneja la instalación del controlador específico de Chrome,
    la configuración y limpieza con un manejo adecuado de errores.
    Asegura un comportamiento consistente del navegador Chrome en diferentes
    aplicaciones.
    """

    def __init__(self) -> None:
        pass

    def _configure_chrome_options(self):
        """
        Configura las opciones de Chrome para un rendimiento óptimo.

        Returns:
            ChromeOptions: Las opciones de Chrome configuradas.
        """
        options = webdriver.ChromeOptions()

        # Agregar opciones de Chrome (ahora como lista)
        for option in BROWSER_CONFIG["chrome"]["options"]:
            if option:  # Solo agregar opciones no vacías
                options.add_argument(option)

        # Agregar preferencias de Chrome
        if "prefs" in BROWSER_CONFIG["chrome"]:
            options.add_experimental_option("prefs", BROWSER_CONFIG["chrome"]["prefs"])

        return options

    def _get_driver_path(self, local=False):
        """
        Recupera la ruta al ejecutable de ChromeDriver.

        Returns:
            str: La ruta al ejecutable de ChromeDriver.
        """
        if local:
            return "driver/chromedriver.exe"
        return ChromeDriverManager().install()

    def create_driver(self) -> webdriver.Chrome:
        """
        Crea y configura una nueva instancia de Chrome WebDriver.

        Returns:
            webdriver.Chrome: La instancia configurada de Chrome WebDriver.

        Raises:
            WebDriverException: Si no se encuentra el ejecutable de ChromeDriver.
        """
        try:
            # Instalar o usar ChromeDriver en caché
            driver_path = self._get_driver_path(local=False)
            self._service = Service(driver_path)

            # Configurar opciones de Chrome
            options = self._configure_chrome_options()

            # Crear instancia de Chrome WebDriver
            self._driver = webdriver.Chrome(service=self._service, options=options)

            # Configurar tiempos de espera específicos de Chrome
            self._driver.set_page_load_timeout(DEFAULT_PAGE_LOAD_TIMEOUT)
            self._driver.implicitly_wait(DEFAULT_ELEMENT_TIMEOUT)

            logging.info("Chrome WebDriver creado exitosamente")

            return self._driver

        except WebDriverException as e:
            logging.error(f"Error al crear Chrome WebDriver: {e}")
            raise e

        except Exception as e:
            logging.error(f"Error inesperado al crear Chrome WebDriver: {e}")
            raise e

    def quit_driver(self) -> None:
        """
        Cierra de forma segura la instancia de Chrome WebDriver.

        Este método asegura una limpieza adecuada de los recursos
        del navegador y previene cualquier problema potencial.
        """
        try:
            if self._driver:
                self._driver.quit()
                logging.info("Chrome WebDriver cerrado exitosamente")
        except Exception as e:
            logging.error(f"Error al cerrar Chrome WebDriver: {e}")
            raise e
        finally:
            self._driver = None
            self._service = None

    def __enter__(self) -> webdriver.Chrome:
        """
        Punto de entrada del gestor de contexto.

        Returns:
            webdriver.Chrome: La instancia de Chrome WebDriver.
        """
        return self.create_driver()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Punto de salida del gestor de contexto.

        Cierra de forma segura la instancia de Chrome WebDriver.
        """
        self.quit_driver()
