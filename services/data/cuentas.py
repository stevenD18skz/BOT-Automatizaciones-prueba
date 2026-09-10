"""Números de cuenta escritos a mano en la UI: separarlos y validarlos.

Lo usan la UI (para avisar al instante) y el Bot (que no puede fiarse de lo que
llegue por el WebSocket). No importa nada pesado, para que la UI pueda usarlo.
"""

from __future__ import annotations

import re
from typing import Iterable

MAX_CUENTAS_POR_CONSULTA = 100

_SEPARADORES = re.compile(r"[\s,;]+")
_SOLO_DIGITOS = re.compile(r"[0-9]{1,30}")


def separar(texto: str) -> list[str]:
    """Una cuenta por línea, o separadas por comas, punto y coma o espacios."""
    return [parte for parte in _SEPARADORES.split(texto or "") if parte]


def limpiar_cuentas(valores: str | Iterable[str]) -> tuple[list[str], list[str]]:
    """Devuelve (válidas sin duplicados y en orden, inválidas tal como llegaron).

    Acepta guiones como separador visual (001-002 -> 001002). Si llega un texto
    en vez de una lista, se separa primero: iterarlo daría carácter a carácter.
    """
    if isinstance(valores, str):
        valores = separar(valores)
    validas: list[str] = []
    invalidas: list[str] = []
    vistas: set[str] = set()
    for bruto in valores:
        original = str(bruto).strip()
        valor = original.replace("-", "")
        if not valor:
            continue
        if not _SOLO_DIGITOS.fullmatch(valor):
            invalidas.append(original)
            continue
        if valor not in vistas:
            vistas.add(valor)
            validas.append(valor)
    return validas, invalidas
