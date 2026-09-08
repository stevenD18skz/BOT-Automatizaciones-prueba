import re
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

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

            is_success, error = self._check_login_success()
            if not is_success:
                failed_msg = MESSAGES["process"]["failed"].format(
                    name="SIIFLoginProcess", error=error
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

    def _check_login_success(self) -> tuple[bool, str]:
        """Espera al menú (éxito) o a la página de error de SIIF (fallo).

        Vigilar las dos salidas es lo que evita que un login rechazado agote
        DEFAULT_LOGIN_TIMEOUT completo esperando un menú que nunca llegará.

        Returns:
            (True, "") si apareció el menú; (False, motivo) si SIIF rechazó.
        """

        def resultado(driver):
            if "ERROR1.ASP" in driver.current_url.upper():
                return "error"
            if driver.find_elements(By.ID, "menu"):
                return "menu"
            return False

        try:
            estado = WebDriverWait(
                self.page.driver, DEFAULT_LOGIN_TIMEOUT, poll_frequency=0.5
            ).until(resultado)
        except TimeoutException:
            return False, "No se detectó el menú principal"

        if estado == "menu":
            return True, ""
        return False, self._leer_error_siif()

    def _leer_error_siif(self) -> str:
        """Extrae el mensaje de la pantalla de errores de SIIF.

        La tabla del error tarda un instante más que el encabezado, así que se
        reintenta hasta ver una línea con código (p. ej. "SFI0048 Usuario no
        existe en el sistema").
        """
        patron = re.compile(r"^[A-Z]{2,5}\d{3,5}\b.+")
        deadline = time.time() + 5
        texto = ""
        while time.time() < deadline:
            try:
                texto = self.page.driver.find_element(By.TAG_NAME, "body").text
            except Exception:
                self.page.logger.warning("No se pudo leer el error de SIIF", exc_info=True)
                break
            for linea in (line.strip() for line in texto.splitlines()):
                if patron.match(linea):
                    return linea
            time.sleep(0.3)
        return "SIIF rechazó el inicio de sesión"
