"""
Utilidades helper para el framework RPA Core

Este módulo proporciona funciones de apoyo que utilizan las constantes
definidas para realizar tareas comunes de manera consistente.
"""

import re
from typing import List, Optional, Tuple

from selenium.webdriver.remote.webdriver import WebDriver

from ..constants import COMMON_SELECTORS, MESSAGES, REGEX_PATTERNS


def find_common_element(
    driver: WebDriver, element_type: str, timeout: int = 10
) -> Optional[Tuple[str, str]]:
    """
    Busca un elemento común usando los selectores predefinidos.

    Args:
        driver: WebDriver instance
        element_type: Tipo de elemento ('search_inputs', 'submit_buttons', etc.)
        timeout: Tiempo máximo de espera

    Returns:
        Optional[Tuple[str, str]]: (by, selector) si encuentra, None si no
    """
    from .waiters import is_element_present

    if element_type not in COMMON_SELECTORS:
        return None

    selectors = COMMON_SELECTORS[element_type]

    for by, selector in selectors:
        if is_element_present(
            driver, by, selector, timeout=2
        ):  # Timeout corto para cada uno
            return (by, selector)

    return None


def validate_email(email: str) -> bool:
    """
    Valida si un email tiene formato correcto.

    Args:
        email: Email a validar

    Returns:
        bool: True si es válido
    """
    if not email or not isinstance(email, str):
        return False

    return bool(re.match(REGEX_PATTERNS["email"], email.strip()))


def validate_url(url: str) -> bool:
    """
    Valida si una URL tiene formato correcto.

    Args:
        url: URL a validar

    Returns:
        bool: True si es válida
    """
    if not url or not isinstance(url, str):
        return False

    return bool(re.match(REGEX_PATTERNS["url"], url.strip()))


def format_message(message_type: str, message_key: str, **kwargs) -> str:
    """
    Formatea un mensaje usando las plantillas predefinidas.

    Args:
        message_type: Tipo de mensaje ('validation', 'navigation', etc.)
        message_key: Clave del mensaje específico
        **kwargs: Parámetros para formatear el mensaje

    Returns:
        str: Mensaje formateado
    """
    try:
        template = MESSAGES[message_type][message_key]
        return template.format(**kwargs)
    except (KeyError, TypeError):
        return f"Mensaje no encontrado: {message_type}.{message_key}"


def smart_search(
    driver: WebDriver, search_term: str, timeout: int = 10
) -> Tuple[bool, str]:
    """
    Realiza búsqueda inteligente usando selectores comunes.

    Args:
        driver: WebDriver instance
        search_term: Término a buscar
        timeout: Tiempo máximo de espera

    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    from .waiters import wait_and_click, wait_and_input_text

    try:
        # 1. Encontrar campo de búsqueda
        search_element = find_common_element(driver, "search_inputs", timeout)
        if not search_element:
            return False, "No se encontró campo de búsqueda"

        # 2. Ingresar término de búsqueda
        by, selector = search_element
        wait_and_input_text(driver, by, selector, search_term, timeout)

        # 3. Encontrar botón de envío
        submit_element = find_common_element(driver, "submit_buttons", timeout)
        if submit_element:
            by, selector = submit_element
            wait_and_click(driver, by, selector, timeout)
        else:
            # Fallback: presionar Enter
            from selenium.webdriver.common.keys import Keys

            from .waiters import wait_for_element_present

            element = wait_for_element_present(driver, by, selector, timeout)
            element.send_keys(Keys.RETURN)

        return True, f"Búsqueda realizada para: {search_term}"

    except Exception as e:
        return False, f"Error en búsqueda inteligente: {str(e)}"


def check_page_errors(driver: WebDriver, timeout: int = 5) -> Tuple[bool, List[str]]:
    """
    Verifica si la página tiene indicadores de error comunes.

    Args:
        driver: WebDriver instance
        timeout: Tiempo máximo de espera por indicador

    Returns:
        Tuple[bool, List[str]]: (tiene_errores, lista_de_errores_encontrados)
    """
    from .waiters import is_element_present

    errors_found = []
    error_selectors = COMMON_SELECTORS["error_indicators"]

    for by, selector in error_selectors:
        if is_element_present(driver, by, selector, timeout=1):  # Timeout corto
            errors_found.append(f"Error encontrado: {selector}")

    return len(errors_found) > 0, errors_found


def check_page_success(driver: WebDriver, timeout: int = 5) -> Tuple[bool, List[str]]:
    """
    Verifica si la página tiene indicadores de éxito comunes.

    Args:
        driver: WebDriver instance
        timeout: Tiempo máximo de espera por indicador

    Returns:
        Tuple[bool, List[str]]: (tiene_éxito, lista_de_éxitos_encontrados)
    """
    from .waiters import is_element_present

    success_found = []
    success_selectors = COMMON_SELECTORS["success_indicators"]

    for by, selector in success_selectors:
        if is_element_present(driver, by, selector, timeout=1):  # Timeout corto
            success_found.append(f"Éxito encontrado: {selector}")

    return len(success_found) > 0, success_found


def wait_for_page_ready(driver: WebDriver, timeout: int = 30) -> bool:
    """
    Espera hasta que la página esté completamente lista.

    Args:
        driver: WebDriver instance
        timeout: Tiempo máximo de espera

    Returns:
        bool: True si la página está lista
    """
    import time

    from .waiters import is_element_present, wait_for_page_load

    try:
        # 1. Esperar carga básica de DOM
        if not wait_for_page_load(driver, timeout // 3):
            return False

        # 2. Esperar que desaparezcan indicadores de carga
        loading_selectors = COMMON_SELECTORS["loading_indicators"]
        start_time = time.time()

        while time.time() - start_time < timeout:
            loading_found = False

            for by, selector in loading_selectors:
                if is_element_present(driver, by, selector, timeout=1):
                    loading_found = True
                    break

            if not loading_found:
                return True

            time.sleep(1)

        return True  # Si no hay indicadores de carga, consideramos que está listo

    except Exception:
        return False


def get_page_info(driver: WebDriver) -> dict:
    """
    Obtiene información básica de la página actual.

    Args:
        driver: WebDriver instance

    Returns:
        dict: Información de la página
    """
    try:
        # Información básica
        info = {
            "url": driver.current_url,
            "title": driver.title,
            "ready_state": driver.execute_script("return document.readyState"),
        }

        # Verificar errores y éxitos
        has_errors, error_details = check_page_errors(driver)
        has_success, success_details = check_page_success(driver)

        info.update(
            {
                "has_errors": has_errors,
                "error_details": error_details,
                "has_success": has_success,
                "success_details": success_details,
            }
        )

        return info

    except Exception as e:
        return {"error": f"No se pudo obtener información de la página: {str(e)}"}


def validate_form_data(form_data: dict, required_fields: List[str]) -> Tuple[bool, str]:
    """
    Valida datos de formulario con reglas comunes.

    Args:
        form_data: Datos del formulario
        required_fields: Campos requeridos

    Returns:
        Tuple[bool, str]: (es_válido, mensaje)
    """
    if not isinstance(form_data, dict):
        return False, "form_data debe ser un diccionario"

    # Verificar campos requeridos
    missing_fields = [field for field in required_fields if field not in form_data]
    if missing_fields:
        return False, format_message(
            "validation", "missing_params", params=", ".join(missing_fields)
        )

    # Verificar campos vacíos
    empty_fields = [
        field
        for field in required_fields
        if not form_data[field]
        or (isinstance(form_data[field], str) and not form_data[field].strip())
    ]
    if empty_fields:
        return False, format_message(
            "validation", "empty_params", params=", ".join(empty_fields)
        )

    # Validaciones específicas
    if "email" in form_data and not validate_email(form_data["email"]):
        return False, format_message(
            "validation", "invalid_email", email=form_data["email"]
        )

    if "url" in form_data and not validate_url(form_data["url"]):
        return False, format_message("validation", "invalid_url", url=form_data["url"])

    return True, "Datos válidos"
