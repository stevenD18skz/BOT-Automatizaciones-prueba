import time
from typing import List

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import Select, WebDriverWait


def wait_and_click(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 30,
) -> None:
    """
    Espera hasta que el elemento sea clickeable, hace scrollIntoView
    y clickea. Si falla con ElementClickInterceptedException, intenta
    un click por JavaScript.

    Parámetros:
    - by: método de localización ('xpath', 'css selector', etc.)
    - locator: selector asociado al método
    """
    wait = WebDriverWait(driver, timeout)
    elem = wait.until(EC.element_to_be_clickable((by, locator)))
    driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", elem)
    try:
        elem.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", elem)


def wait_and_input_text(
    driver: WebDriver,
    by: str,
    locator: str,
    text: str,
    timeout: int = 30,
    poll_frequency: float = 0.5,
    scroll_into_view: bool = True,
) -> None:
    """
    Espera hasta que el elemento sea visible y esté habilitado.
    - Ignora NoSuchElementException y StaleElementReferenceException.
    - Hace scrollIntoView antes de devolver el elemento.
    """
    wait = WebDriverWait(driver, timeout)
    elem = wait.until(EC.element_to_be_clickable((by, locator)))
    if scroll_into_view:
        driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", elem)
    elem.clear()
    elem.send_keys(text)


def wait_for_element(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 10,
    poll_frequency: float = 0.5,
    scroll_into_view: bool = True,
) -> WebElement:
    """
    Espera hasta que el elemento sea visible y esté habilitado.
    - Ignora NoSuchElementException y StaleElementReferenceException.
    - Hace scrollIntoView antes de devolver el elemento.

    Parámetros:
    - by: método de localización ('xpath', 'css selector', etc.)
    - locator: selector asociado al método
    """
    wait = WebDriverWait(
        driver,
        timeout,
        poll_frequency=poll_frequency,
        ignored_exceptions=[NoSuchElementException, StaleElementReferenceException],
    )

    elem = wait.until(EC.visibility_of_element_located((by, locator)))
    if scroll_into_view:
        driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", elem)
    return elem


def wait_for_element_present(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 10,
) -> WebElement:
    """
    Espera hasta que el elemento esté presente en el DOM (no necesariamente visible).

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        timeout: Tiempo máximo de espera

    Returns:
        WebElement: Elemento encontrado
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, locator)))


def wait_for_elements_present(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 10,
) -> List[WebElement]:
    """
    Espera hasta que al menos un elemento esté presente en el DOM.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector de los elementos
        timeout: Tiempo máximo de espera

    Returns:
        List[WebElement]: Lista de elementos encontrados
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_all_elements_located((by, locator)))


def wait_for_element_clickable(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 10,
) -> WebElement:
    """
    Espera hasta que el elemento sea clickeable.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        timeout: Tiempo máximo de espera

    Returns:
        WebElement: Elemento clickeable
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable((by, locator)))


def wait_for_element_visible(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 10,
) -> WebElement:
    """
    Espera hasta que el elemento sea visible.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        timeout: Tiempo máximo de espera

    Returns:
        WebElement: Elemento visible
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.visibility_of_element_located((by, locator)))


def wait_for_element_invisible(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 10,
) -> bool:
    """
    Espera hasta que el elemento sea invisible.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        timeout: Tiempo máximo de espera

    Returns:
        bool: True si el elemento es invisible

    Raises:
        TimeoutException: Si el elemento sigue siendo visible después del timeout
    """
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.invisibility_of_element_located((by, locator)))
        return True
    except TimeoutException:
        return False


def wait_and_get_text(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 10,
    retry_interval: float = 0.5,
    default_text: str = "",
) -> str:
    """
    Espera a que un elemento tenga texto visible y lo retorna.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        timeout: Tiempo máximo de espera
        retry_interval: Intervalo entre intentos
        default_text: Texto por defecto si no se encuentra

    Returns:
        str: Texto del elemento o default_text
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            element = wait_for_element_present(driver, by, locator, 2)
            text = element.text.strip()

            if text:
                return text

            time.sleep(retry_interval)

        except TimeoutException:
            time.sleep(retry_interval)

    return default_text


def wait_and_get_text_from_input(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 10,
) -> str | None:
    """
    Espera hasta que el elemento esté presente y obtiene su valor
    por el atributo de value.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        timeout: Tiempo máximo de espera

    Returns:
        str: Valor del atributo value
        None: Si el elemento no tiene atributo value
    """

    element = wait_for_element_present(driver, by, locator, timeout)
    return element.get_attribute("value")


def wait_and_get_attribute(
    driver: WebDriver,
    by: str,
    locator: str,
    attribute: str,
    timeout: int = 10,
) -> str:
    """
    Espera hasta que el elemento esté presente y obtiene su atributo.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        attribute: Nombre del atributo
        timeout: Tiempo máximo de espera

    Returns:
        str: Valor del atributo
    """
    element = wait_for_element_present(driver, by, locator, timeout)
    value = element.get_attribute(attribute)
    return value or ""


def wait_and_select_dropdown_by_text(
    driver: WebDriver,
    by: str,
    locator: str,
    text: str,
    timeout: int = 10,
) -> None:
    """
    Espera hasta que el dropdown sea clickeable y selecciona por texto visible.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del dropdown
        text: Texto visible de la opción
        timeout: Tiempo máximo de espera
    """
    element = wait_for_element_clickable(driver, by, locator, timeout)
    select = Select(element)
    select.select_by_visible_text(text)


def wait_and_select_dropdown_by_value(
    driver: WebDriver,
    by: str,
    locator: str,
    value: str,
    timeout: int = 10,
) -> None:
    """
    Espera hasta que el dropdown sea clickeable y selecciona por valor.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del dropdown
        value: Valor de la opción
        timeout: Tiempo máximo de espera
    """
    element = wait_for_element_clickable(driver, by, locator, timeout)
    select = Select(element)
    select.select_by_value(value)


def is_element_present(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 5,
) -> bool:
    """
    Verifica si un elemento está presente sin lanzar excepción.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        timeout: Tiempo máximo de espera

    Returns:
        bool: True si el elemento está presente
    """
    try:
        wait_for_element_present(driver, by, locator, timeout)
        return True
    except TimeoutException:
        return False


def is_element_clickable(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 5,
) -> bool:
    """
    Verifica si un elemento es clickeable sin lanzar excepción.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        timeout: Tiempo máximo de espera

    Returns:
        bool: True si el elemento es clickeable
    """
    try:
        wait_for_element_clickable(driver, by, locator, timeout)
        return True
    except TimeoutException:
        return False


def wait_for_page_load(driver: WebDriver, timeout: int = 30) -> bool:
    """
    Espera a que la página termine de cargar completamente.

    Args:
        driver: WebDriver instance
        timeout: Tiempo máximo de espera

    Returns:
        bool: True si la página cargó completamente
    """
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except TimeoutException:
        return False


def wait_for_url_contains(
    driver: WebDriver,
    url_part: str,
    timeout: int = 10,
) -> bool:
    """
    Espera a que la URL contenga una parte específica.

    Args:
        driver: WebDriver instance
        url_part: Parte de URL a esperar
        timeout: Tiempo máximo de espera

    Returns:
        bool: True si la URL contiene la parte especificada
    """
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.url_contains(url_part))
        return True
    except TimeoutException:
        return False


def scroll_to_element(
    driver: WebDriver,
    by: str,
    locator: str,
    timeout: int = 10,
) -> None:
    """
    Espera hasta que el elemento esté presente y hace scroll hacia él.

    Args:
        driver: WebDriver instance
        by: Método de localización
        locator: Selector del elemento
        timeout: Tiempo máximo de espera
    """
    element = wait_for_element_present(driver, by, locator, timeout)
    driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", element)


def wait_for_alert_present(driver: WebDriver, timeout: int = 10) -> bool:
    """
    Espera a que aparezca una alerta.

    Args:
        driver: WebDriver instance
        timeout: Tiempo máximo de espera

    Returns:
        bool: True si aparece una alerta
    """
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.alert_is_present())
        return True
    except TimeoutException:
        return False
