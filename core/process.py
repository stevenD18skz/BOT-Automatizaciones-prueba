"""
Clase base para procesos RPA

Este módulo proporciona la implementación base para procesos RPA que trabajan
con páginas web usando Selenium WebDriver.
"""

import logging
from typing import Any, Dict

from selenium.webdriver.remote.webdriver import WebDriver

from .base import BasePage
from .interfaces import ProcessInterface


class BaseProcess(ProcessInterface):
    """
    Clase base para procesos RPA que interactúan con páginas web.

    Combina la funcionalidad de BasePage con la interfaz ProcessInterface
    para proporcionar una base sólida para la implementación de procesos RPA.

    Atributos:
        driver (WebDriver): La instancia de WebDriver
        page (BasePage): Instancia de la página base para interacciones web
        logger (logging.Logger): Logger para el proceso
        _variables (Dict[str, Any]): Variables internas del proceso
    """

    def __init__(self, driver: WebDriver):
        """
        Inicializa el proceso base.

        Args:
            driver (WebDriver): La instancia de WebDriver
        """
        self.driver = driver
        self.page = BasePage(driver)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._variables: Dict[str, Any] = {}

    def execute(self, **kwargs) -> tuple[bool, str]:
        """
        Método abstracto que debe ser implementado por las clases hijas.

        Args:
            **kwargs: Parámetros específicos del proceso

        Returns:
            tuple[bool, str]: (éxito, mensaje)
        """
        raise NotImplementedError("Subclases deben implementar el método execute")

    def _log_execution_start(self, **kwargs) -> None:
        """
        Registra el inicio de la ejecución del proceso.

        Args:
            **kwargs: Parámetros del proceso para logging
        """
        process_name = self.__class__.__name__
        self.logger.info(f"Iniciando ejecución del proceso: {process_name}")
        if kwargs:
            self.logger.debug(f"Parámetros: {kwargs}")

    def _log_execution_end(self, success: bool, message: str) -> None:
        """
        Registra el final de la ejecución del proceso.

        Args:
            success (bool): Si el proceso fue exitoso
            message (str): Mensaje del resultado
        """
        process_name = self.__class__.__name__
        level = logging.INFO if success else logging.ERROR
        status = "exitoso" if success else "falló"
        self.logger.log(level, f"Proceso {process_name} {status}: {message}")

    def _handle_exception(self, exception: Exception) -> tuple[bool, str]:
        """
        Maneja excepciones durante la ejecución del proceso.

        Args:
            exception (Exception): La excepción capturada

        Returns:
            tuple[bool, str]: (False, mensaje de error)
        """
        # El detalle técnico completo va al log (exc_info); el mensaje que llega a
        # la UI, a los Excel y a la trazabilidad debe poder leerlo una persona.
        from core.utils.errores import mensaje_legible

        error_message = f"Error en proceso {self.__class__.__name__}: {mensaje_legible(exception)}"
        self.logger.error(error_message, exc_info=True)
        return False, error_message

    def clear_variables(self) -> None:
        """
        Limpia todas las variables del proceso.
        """
        self._variables.clear()
        self.logger.debug("Variables del proceso limpiadas")

    def get_page(self) -> BasePage:
        """
        Obtiene la instancia de la página base.

        Returns:
            BasePage: La instancia de la página base
        """
        return self.page

    def wait_for_condition(
        self, condition_func, timeout: int = 10, interval: float = 0.5
    ) -> bool:
        """
        Espera hasta que una condición personalizada se cumpla.

        Args:
            condition_func: Función que retorna bool cuando la condición se cumple
            timeout: Tiempo máximo de espera en segundos
            interval: Intervalo entre verificaciones en segundos

        Returns:
            bool: True si la condición se cumplió, False si timeout
        """
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    return True
            except Exception as e:
                self.logger.debug(f"Condición falló con excepción: {e}")

            time.sleep(interval)

        return False

    def retry_action(
        self, action_func, max_retries: int = 3, delay: float = 1.0
    ) -> tuple[bool, str]:
        """
        Reintenta una acción hasta que sea exitosa o se agoten los intentos.

        Args:
            action_func: Función a ejecutar que retorna tuple[bool, str]
            max_retries: Número máximo de reintentos
            delay: Delay entre reintentos en segundos

        Returns:
            tuple[bool, str]: Resultado de la última ejecución
        """
        import time

        for attempt in range(max_retries + 1):
            try:
                success, message = action_func()
                if success:
                    return True, message

                if attempt < max_retries:
                    self.logger.warning(
                        f"Intento {attempt + 1} falló: {message}. Reintentando..."
                    )
                    time.sleep(delay)
                else:
                    return False, f"Falló después de {max_retries} intentos: {message}"

            except Exception as e:
                error_msg = f"Excepción en intento {attempt + 1}: {str(e)}"
                if attempt < max_retries:
                    self.logger.warning(f"{error_msg}. Reintentando...")
                    time.sleep(delay)
                else:
                    return (
                        False,
                        f"Falló después de {max_retries} intentos con excepción: {str(e)}",
                    )

        return False, "Número inesperado de intentos"

    def validate_inputs(self, required_params: list[str], **kwargs) -> tuple[bool, str]:
        """
        Valida que los parámetros requeridos estén presentes y no sean None/vacíos.

        Args:
            required_params: Lista de nombres de parámetros requeridos
            **kwargs: Parámetros a validar

        Returns:
            tuple[bool, str]: (True, "OK") si válido, (False, "Parámetros no válidos") si no
        """
        missing_params = []
        empty_params = []

        for param in required_params:
            if param not in kwargs:
                missing_params.append(param)
            elif kwargs[param] is None or (
                isinstance(kwargs[param], str) and kwargs[param].strip() == ""
            ):
                empty_params.append(param)

        if missing_params or empty_params:
            return False, "Parámetros no válidos"

        return True, "Parámetros válidos"
