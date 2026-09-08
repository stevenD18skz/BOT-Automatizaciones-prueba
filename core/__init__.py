"""
Core framework para automatización RPA con Selenium

Este módulo proporciona las clases y utilidades fundamentales para
la construcción de bots de automatización web robustos y mantenibles.
"""

from .base import BasePage
from .constants import (
    COMMON_SELECTORS,
    DEFAULT_ELEMENT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    MESSAGES,
    PROCESS_STATUS,
    REGEX_PATTERNS,
)
from .driver_manager import ChromeDriver
from .interfaces import ProcessInterface
from .process import BaseProcess

__all__ = [
    "BasePage",
    "ChromeDriver",
    "ProcessInterface",
    "BaseProcess",
    "DEFAULT_TIMEOUT",
    "DEFAULT_ELEMENT_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "COMMON_SELECTORS",
    "MESSAGES",
    "PROCESS_STATUS",
    "REGEX_PATTERNS",
]
