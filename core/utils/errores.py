"""Mensajes de error para personas.

Selenium mete en el texto de sus excepciones el "Session info" y un volcado de
decenas de direcciones de memoria (0xff1213...). Eso va al log, donde
logging.exception lo guarda completo; a la pantalla, a la tabla de resultados, a
los Excel y a la trazabilidad solo llega esta versión legible.
"""

from __future__ import annotations

from selenium.common.exceptions import NoSuchElementException, TimeoutException

_ERRORES_DE_RED = {
    "ERR_CONNECTION_REFUSED": (
        "SIIF rechazó la conexión. Suele ser un corte momentáneo de la red o la VPN: "
        "inténtalo de nuevo."
    ),
    "ERR_CONNECTION_TIMED_OUT": "SIIF no respondió a tiempo. Revisa la red o la VPN.",
    "ERR_CONNECTION_RESET": "La conexión con SIIF se cortó. Inténtalo de nuevo.",
    "ERR_NAME_NOT_RESOLVED": (
        "No se encontró el servidor de SIIF. Revisa que estés en la red del banco o en la VPN."
    ),
    "ERR_ADDRESS_UNREACHABLE": "No se puede llegar al servidor de SIIF. Revisa la red o la VPN.",
    "ERR_INTERNET_DISCONNECTED": "El equipo no tiene conexión de red.",
}

_MAX_CARACTERES = 300


def mensaje_legible(exc: BaseException) -> str:
    texto = str(exc)
    for codigo, mensaje in _ERRORES_DE_RED.items():
        if codigo in texto:
            return mensaje
    if isinstance(exc, TimeoutException):
        return "SIIF tardó demasiado en mostrar el elemento esperado."
    if isinstance(exc, NoSuchElementException):
        return "SIIF no mostró el elemento esperado en la página."

    util = texto.split("Stacktrace:")[0]
    lineas = [
        linea.strip()
        for linea in util.splitlines()
        if linea.strip() and not linea.strip().startswith("(Session info")
    ]
    limpio = " ".join(lineas).removeprefix("Message:").strip()
    if not limpio:
        return type(exc).__name__
    if len(limpio) > _MAX_CARACTERES:
        return limpio[: _MAX_CARACTERES - 1] + "…"
    return limpio
