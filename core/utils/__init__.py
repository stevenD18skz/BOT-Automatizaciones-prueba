"""
Utilidades para el framework RPA

Este módulo contiene utilidades de apoyo para el framework RPA incluyendo:
- Waiters: Funciones de espera robustas para elementos
- Context: Manejadores de contexto para frames
- Logging: Configuración de logging
- Helpers: Funciones utilitarias comunes
"""

from .context import FrameContext
from .helpers import (
    check_page_errors,
    check_page_success,
    find_common_element,
    format_message,
    get_page_info,
    smart_search,
    validate_email,
    validate_form_data,
    validate_url,
    wait_for_page_ready,
)
from .logging import setup_logging
from .waiters import (
    is_element_clickable,
    is_element_present,
    scroll_to_element,
    wait_and_click,
    wait_and_get_attribute,
    wait_and_get_text,
    wait_and_input_text,
    wait_and_select_dropdown_by_text,
    wait_and_select_dropdown_by_value,
    wait_for_alert_present,
    wait_for_element,
    wait_for_element_clickable,
    wait_for_element_invisible,
    wait_for_element_present,
    wait_for_element_visible,
    wait_for_elements_present,
    wait_for_page_load,
    wait_for_url_contains,
)

__all__ = [
    # Context managers
    "FrameContext",
    # Logging
    "setup_logging",
    # Waiters
    "wait_and_click",
    "wait_and_input_text",
    "wait_for_element",
    "wait_for_element_present",
    "wait_for_elements_present",
    "wait_for_element_clickable",
    "wait_for_element_visible",
    "wait_for_element_invisible",
    "wait_and_get_text",
    "wait_and_get_attribute",
    "wait_and_select_dropdown_by_text",
    "wait_and_select_dropdown_by_value",
    "is_element_present",
    "is_element_clickable",
    "wait_for_page_load",
    "wait_for_url_contains",
    "scroll_to_element",
    "wait_for_alert_present",
    # Helpers
    "find_common_element",
    "validate_email",
    "validate_url",
    "format_message",
    "smart_search",
    "check_page_errors",
    "check_page_success",
    "wait_for_page_ready",
    "get_page_info",
    "validate_form_data",
]
