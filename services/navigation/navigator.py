from selenium.webdriver.common.by import By

from config.settings import MENU_ROUTE
from core.base import BasePage


class Navigator:
    def __init__(self, page: BasePage):
        self.page = page

    def navigate(self) -> None:
        """Navega por el menú principal de SIIF."""
        self.page.click((By.ID, MENU_ROUTE["menu"]))
