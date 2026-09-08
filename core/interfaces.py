"""
Interfaces para el framework RPA

Este módulo define las interfaces que deben implementar los diferentes
componentes del framework RPA para asegurar consistencia y contractos.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ProcessInterface(ABC):
    """
    Interfaz base para todos los procesos RPA.

    Define el contrato que deben cumplir todos los procesos:
    - Método execute obligatorio que retorna (bool, str)
    - Capacidad de extraer variables del proceso
    """

    @abstractmethod
    def execute(self, **kwargs) -> tuple[bool, str]:
        """
        Ejecuta el proceso RPA.

        Args:
            **kwargs: Parámetros específicos del proceso

        Returns:
            tuple[bool, str]: (éxito, mensaje)
                - éxito: True si el proceso fue exitoso, False en caso contrario
                - mensaje: Descripción del resultado o error
        """
        pass

    def get_variables(self) -> Dict[str, Any]:
        """
        Extrae variables generadas durante la ejecución del proceso.

        Returns:
            Dict[str, Any]: Diccionario con las variables extraídas
        """
        return getattr(self, "_variables", {})

    def set_variable(self, key: str, value: Any) -> None:
        """
        Establece una variable en el proceso.

        Args:
            key (str): Nombre de la variable
            value (Any): Valor de la variable
        """
        if not hasattr(self, "_variables"):
            self._variables = {}
        self._variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        """
        Obtiene una variable del proceso.

        Args:
            key (str): Nombre de la variable
            default (Any): Valor por defecto si la variable no existe

        Returns:
            Any: El valor de la variable o el valor por defecto
        """
        return getattr(self, "_variables", {}).get(key, default)
