"""
Patrón Base de Objetos de Página

Este módulo proporciona la clase base para todos los objetos de página en el framework RPA.
Implementa funcionalidades comunes y utilidades para la interacción con páginas web.
"""

import logging

from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from core.constants import DEFAULT_ELEMENT_TIMEOUT

from .utils.waiters import (
    is_element_clickable,
    is_element_present,
    scroll_to_element,
    wait_and_click,
    wait_and_get_attribute,
    wait_and_get_text,
    wait_and_get_text_from_input,
    wait_and_input_text,
    wait_and_select_dropdown_by_text,
    wait_and_select_dropdown_by_value,
    wait_for_alert_present,
    wait_for_element,
    wait_for_element_invisible,
    wait_for_element_present,
    wait_for_element_visible,
    wait_for_elements_present,
    wait_for_page_load,
    wait_for_url_contains,
)


class BasePage:
    """
    Clase base para todos los objetos de página.

    Esta clase proporciona funcionalidad común para la interacción con páginas web, incluyendo:
    - Espera y búsqueda de elementos
    - Acciones comunes (clic, entrada de texto, etc.)
    - Manejo de errores
    - Registro de eventos

    Atributos:
        driver (WebDriver): La instancia de WebDriver
        wait (WebDriverWait): Utilidad de espera para elementos
    """

    driver: WebDriver
    logger: logging.Logger

    def __init__(self, driver: WebDriver):
        """
        Inicializa la página base.

        Args:
            driver (WebDriver): La instancia de WebDriver
        """
        self.driver = driver
        self.logger = logging.getLogger(self.__class__.__name__)

    def find_element(self, locator: tuple[str, str]) -> WebElement:
        """
        Encuentra un elemento con espera explícita.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor

        Returns:
            WebElement: El elemento encontrado

        Raises:
            TimeoutException: Si el elemento no se encuentra dentro del tiempo de espera
        """
        try:
            by, value = locator
            return wait_for_element_present(
                self.driver, by, value, DEFAULT_ELEMENT_TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"Elemento no encontrado: {locator}, e: {e}")
            raise

    def find_elements(self, locator: tuple[str, str]) -> list[WebElement]:
        """
        Encuentra múltiples elementos con espera explícita.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor

        Returns:
            list[WebElement]: Lista de elementos encontrados
        """
        try:
            by, value = locator
            return wait_for_elements_present(
                self.driver, by, value, DEFAULT_ELEMENT_TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"Elementos no encontrados: {locator}, e: {e}")
            return []

    def click(self, locator: tuple[str, str]) -> None:
        """
        Hace clic en un elemento con espera explícita usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
        """
        try:
            by, value = locator
            wait_and_click(self.driver, by, value, DEFAULT_ELEMENT_TIMEOUT)
            self.logger.debug(f"Clic en elemento: {locator}")
        except Exception as e:
            self.logger.error(f"Error al hacer clic en elemento: {locator}, e: {e}")
            raise

    def input_text(self, locator: tuple[str, str], text: str) -> None:
        """
        Ingresa texto en un elemento usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
            text (str): El texto a ingresar
        """
        try:
            by, value = locator
            wait_and_input_text(self.driver, by, value, text, DEFAULT_ELEMENT_TIMEOUT)
            self.logger.debug(f"Texto ingresado '{text}' en elemento: {locator}")
        except Exception as e:
            self.logger.error(f"Error al ingresar texto en elemento: {locator}, e: {e}")
            raise

    def wait_for_element(
        self, locator: tuple[str, str], timeout: int = DEFAULT_ELEMENT_TIMEOUT
    ) -> WebElement:
        """
        Espera hasta que el elemento sea visible usando waiters centralizados.
        """
        by, value = locator
        return wait_for_element(self.driver, by, value, timeout)

    def get_text(self, locator: tuple[str, str]) -> str:
        """
        Obtiene texto de un elemento usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor

        Returns:
            str: El texto del elemento
        """
        try:
            by, value = locator
            return wait_and_get_text(self.driver, by, value, DEFAULT_ELEMENT_TIMEOUT)
        except Exception as e:
            self.logger.error(f"Error al obtener texto del elemento: {locator}, e: {e}")
            raise

    def get_text_from_input(self, locator: tuple[str, str]) -> str:
        """
        Obtiene texto de un elemento usando waiters centralizados.
        Si el elemento no tiene atributo value, retorna una cadena vacía.
        """
        by, value = locator
        text = wait_and_get_text_from_input(
            self.driver, by, value, DEFAULT_ELEMENT_TIMEOUT
        )
        if text:
            return text
        else:
            return ""

    def wait_get_text(
        self,
        locator: tuple[str, str],
        timeout: int = 10,
        retry_interval: float = 0.5,
        default_text: str = "",
    ) -> str:
        """
        Espera a que un elemento tenga texto visible usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
            timeout (int): Tiempo máximo de espera en segundos
            retry_interval (float): Intervalo entre intentos en segundos
            default_text (str): Texto a retornar si no se encuentra texto en el elemento

        Returns:
            str: El texto del elemento o default_text si no se encuentra
        """
        by, value = locator
        return wait_and_get_text(
            self.driver, by, value, timeout, retry_interval, default_text
        )

    def change_frame(self, name: str) -> None:
        """
        Cambia a un frame con espera explícita.

        Args:
            name (str): El nombre del frame
        """
        try:
            self.driver.switch_to.frame(name)
        except (TimeoutException, WebDriverException) as e:
            self.logger.error(f"Error al cambiar al frame: {name}, e: {e}")
            raise

    def change_frame_default(self) -> None:
        """
        Cambia al frame por defecto.
        """
        self.driver.switch_to.default_content()

    def accept_alert(self) -> None:
        """
        Acepta una alerta usando waiters centralizados.
        """
        try:
            if wait_for_alert_present(self.driver, DEFAULT_ELEMENT_TIMEOUT):
                self.driver.switch_to.alert.accept()
                self.logger.debug("Alerta aceptada")
            else:
                raise Exception("No se encontró alerta para aceptar")
        except Exception as e:
            self.logger.error(f"Error al aceptar alerta, e: {e}")
            raise

    def navigate_to(self, url: str) -> None:
        """
        Navega a una URL.
        """
        self.driver.get(url)
        self.logger.debug(f"Navegando a: {url}")

    def is_element_present(self, locator: tuple[str, str]) -> bool:
        """
        Verifica si un elemento está presente usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor

        Returns:
            bool: True si el elemento está presente, False en caso contrario
        """
        by, value = locator
        return is_element_present(self.driver, by, value, DEFAULT_ELEMENT_TIMEOUT)

    def wait_for_element_visible(self, locator: tuple[str, str]) -> None:
        """
        Espera a que un elemento sea visible usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
        """
        try:
            by, value = locator
            wait_for_element_visible(self.driver, by, value, DEFAULT_ELEMENT_TIMEOUT)
            self.logger.debug(f"Elemento visible: {locator}")
        except Exception as e:
            self.logger.error(f"Elemento no visible: {locator}, e: {e}")
            raise

    def wait_for_element_invisible(self, locator: tuple[str, str]) -> None:
        """
        Espera a que un elemento sea invisible usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
        """
        try:
            by, value = locator
            wait_for_element_invisible(self.driver, by, value, DEFAULT_ELEMENT_TIMEOUT)
            self.logger.debug(f"Elemento invisible: {locator}")
        except Exception as e:
            self.logger.error(f"El elemento sigue siendo visible: {locator}, e: {e}")
            raise

    def select_dropdown_by_text(self, locator: tuple[str, str], text: str) -> None:
        """
        Selecciona una opción de un dropdown por texto visible usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
            text (str): El texto visible de la opción a seleccionar
        """
        try:
            by, value = locator
            wait_and_select_dropdown_by_text(
                self.driver, by, value, text, DEFAULT_ELEMENT_TIMEOUT
            )
            self.logger.debug(f"Seleccionado '{text}' en dropdown: {locator}")
        except Exception as e:
            self.logger.error(
                f"Error al seleccionar en dropdown: {locator}, texto: {text}, e: {e}"
            )
            raise

    def select_dropdown_by_value(self, locator: tuple[str, str], value: str) -> None:
        """
        Selecciona una opción de un dropdown por valor usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
            value (str): El valor de la opción a seleccionar
        """
        try:
            by, loc_value = locator
            wait_and_select_dropdown_by_value(
                self.driver, by, loc_value, value, DEFAULT_ELEMENT_TIMEOUT
            )
            self.logger.debug(f"Seleccionado valor '{value}' en dropdown: {locator}")
        except Exception as e:
            self.logger.error(
                f"Error al seleccionar valor en dropdown: {locator}, valor: {value}, e: {e}"
            )
            raise

    def get_attribute(self, locator: tuple[str, str], attribute: str) -> str:
        """
        Obtiene el valor de un atributo de un elemento usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
            attribute (str): El nombre del atributo

        Returns:
            str: El valor del atributo
        """
        try:
            by, value = locator
            result = wait_and_get_attribute(
                self.driver, by, value, attribute, DEFAULT_ELEMENT_TIMEOUT
            )
            self.logger.debug(f"Atributo '{attribute}' obtenido: {result}")
            return result
        except Exception as e:
            self.logger.error(
                f"Error al obtener atributo: {locator}, atributo: {attribute}, e: {e}"
            )
            raise

    def is_element_clickable(self, locator: tuple[str, str], timeout: int = 5) -> bool:
        """
        Verifica si un elemento es clickeable usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
            timeout (int): Tiempo de espera en segundos

        Returns:
            bool: True si el elemento es clickeable, False en caso contrario
        """
        by, value = locator
        return is_element_clickable(self.driver, by, value, timeout)

    def scroll_to_element(self, locator: tuple[str, str]) -> None:
        """
        Hace scroll hasta un elemento específico usando waiters centralizados.

        Args:
            locator (tuple[str, str]): La estrategia de localización y su valor
        """
        try:
            by, value = locator
            scroll_to_element(self.driver, by, value, DEFAULT_ELEMENT_TIMEOUT)
            self.logger.debug(f"Scroll realizado al elemento: {locator}")
        except Exception as e:
            self.logger.error(f"Error al hacer scroll al elemento: {locator}, e: {e}")
            raise

    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """
        Espera a que la página termine de cargar usando waiters centralizados.

        Args:
            timeout (int): Tiempo máximo de espera en segundos

        Returns:
            bool: True si la página cargó completamente, False en caso contrario
        """
        result = wait_for_page_load(self.driver, timeout)
        if result:
            self.logger.debug("Página cargada completamente")
        else:
            self.logger.warning(f"La página no terminó de cargar en {timeout} segundos")
        return result

    def execute_script(self, script: str, *args):
        """
        Ejecuta JavaScript en el navegador.

        Args:
            script (str): El código JavaScript a ejecutar
            *args: Argumentos para el script

        Returns:
            any: El resultado de la ejecución del script
        """
        try:
            result = self.driver.execute_script(script, *args)
            self.logger.debug(f"Script ejecutado: {script[:50]}...")
            return result
        except Exception as e:
            self.logger.error(f"Error al ejecutar script: {e}")
            raise

    def get_current_url(self) -> str:
        """
        Obtiene la URL actual del navegador.

        Returns:
            str: La URL actual
        """
        return self.driver.current_url

    def get_page_title(self) -> str:
        """
        Obtiene el título de la página actual.

        Returns:
            str: El título de la página
        """
        return self.driver.title

    def refresh_page(self) -> None:
        """
        Actualiza la página actual.
        """
        self.driver.refresh()
        self.logger.debug("Página actualizada")

    def wait_for_url_contains(self, url_part: str, timeout: int = 10) -> bool:
        """
        Espera a que la URL contenga una parte específica usando waiters centralizados.

        Args:
            url_part (str): La parte de URL a esperar
            timeout (int): Tiempo máximo de espera en segundos

        Returns:
            bool: True si la URL contiene la parte especificada, False en caso contrario
        """
        result = wait_for_url_contains(self.driver, url_part, timeout)
        if result:
            self.logger.debug(f"URL contiene: {url_part}")
        else:
            self.logger.warning(
                f"URL no contiene '{url_part}' después de {timeout} segundos"
            )
        return result
