from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from core.constants import DEFAULT_LOGIN_TIMEOUT, MESSAGES
from core.process import BasePage


class SIIFLoginProcess:
    def __init__(self, page: BasePage):
        self.page = page

    def execute(self, username: str = "", password: str = "") -> tuple[bool, str]:
        """
        Ejecuta el proceso de login con credenciales.

        Args:
            username: Usuario para login
            password: Contraseña para login
            **kwargs: Parámetros adicionales
        """
        try:
            if not username or not password:
                failed_msg = "Credenciales no proporcionadas"
                return False, failed_msg

            # Realizar login
            if not self._perform_login(username, password):
                failed_msg = "Error en las credenciales de login"
                return False, failed_msg

            if not self._check_login_success():
                failed_msg = MESSAGES["process"]["failed"].format(
                    name="SIIFLoginProcess",
                    error="No se detectó el menú principal",
                )
                return False, failed_msg

            success_msg = MESSAGES["process"]["success"].format(name="SIIFLoginProcess")
            return True, success_msg

        except Exception:
            return False, "Error en el proceso de Login"

    def _perform_login(self, username: str, password: str) -> bool:
        """
        Realiza el proceso de login con las credenciales.

        Args:
            username: Usuario
            password: Contraseña

        Returns:
            bool: True si el login fue exitoso
        """
        try:
            # Esperar a que aparezcan los campos de login
            self.page.wait_for_element(
                (By.ID, "USUARIO"), DEFAULT_LOGIN_TIMEOUT
            ).send_keys(username)
            self.page.wait_for_element(
                (By.ID, "CONTRASENA"), DEFAULT_LOGIN_TIMEOUT
            ).send_keys(password)

            # Hacer clic en el botón de login
            self.page.click((By.NAME, "Aceptar"))

            return True

        except Exception as e:
            self.page.logger.error(f"Error realizando login: {str(e)}")
            return False

    def _check_login_success(self) -> bool:
        """
        Espera hasta TIMEOUT_LOGIN segundos a que aparezca el menú (id="menu").
        """
        try:
            self.page.wait_for_element((By.ID, "menu"), DEFAULT_LOGIN_TIMEOUT)
            return True
        except TimeoutException:
            return False
