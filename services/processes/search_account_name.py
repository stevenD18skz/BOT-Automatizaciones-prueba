from typing import Any

from selenium.webdriver.common.by import By

from config.settings import MENU_ROUTE
from core import BaseProcess


class SearchAccountName(BaseProcess):
    def execute(self, **data: dict[str, Any]) -> tuple[bool, str]:
        try:
            self._log_execution_start(**data)

            # 0. Validar datos de entrada.
            is_valid, validation_message = self.validate_inputs(
                required_params=["NUMERO_CUENTA"], **data
            )

            if not is_valid:
                return False, validation_message

            # 1. Abrir el menu del proceso.
            self.navigate_to_process()

            # 2. Lógica principal del proceso (ejemplo: buscar nombre de cuenta).
            numero_cuenta = str(data.get("NUMERO_CUENTA", ""))
            is_found, nombre_cuenta = self.search_account_name(numero_cuenta)

            if not is_found:
                return False, nombre_cuenta

            # 3. Guardar resultado en variables del proceso.
            self.set_variable("NOMBRE_CUENTA", nombre_cuenta)

            message = "Proceso ejecutado exitosamente"
            self._log_execution_end(True, message)
            return True, message

        except Exception as e:
            return self._handle_exception(e)

    def search_account_name(self, numero_cuenta: str) -> tuple[bool, str]:
        """
        Método de ejemplo para buscar el nombre de una cuenta dado su número.

        Args:
            numero_cuenta (str): El número de cuenta a buscar

        Returns:
            tuple[bool, str]: (True, nombre de la cuenta) o (False, mensaje de error)
        """
        # Aquí iría la lógica real para buscar el nombre de la cuenta.

        self.page.input_text((By.ID, "N01NPR"), numero_cuenta)

        self.page.click(
            (
                By.NAME,
                "Aceptar1",
            )
        )
        self.page.click(
            (
                By.XPATH,
                "/html/body/form[2]/div/div/div/div[2]/div/table/tbody/tr[2]/td/a",
            )
        )

        name = self.page.get_text(
            (
                By.XPATH,
                "/html/body/form/div/div/div/div[2]/div/table[2]/tbody/tr[1]/td[4]",
            )
        )

        return True, name

    def navigate_to_process(self) -> None:
        """Navega al proceso"""
        self.page.change_frame_default()

        self.page.click((By.ID, MENU_ROUTE["proceso"]))

        self.page.change_frame("contenido")
