from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """
    Clase base abstracta para todas las herramientas (tools) disponibles para el LLM.

    Cada tool debe implementar:
    - get_definition(): Retorna la definición del tool en formato Anthropic
    - execute(): Ejecuta la lógica del tool
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre único del tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción detallada de qué hace el tool y cuándo usarlo."""
        pass

    @abstractmethod
    def get_definition(self) -> Dict[str, Any]:
        """
        Retorna la definición del tool en formato Anthropic API.

        Returns:
            Dict con estructura:
            {
                "name": str,
                "description": str,
                "input_schema": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        """
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la lógica del tool con los parámetros proporcionados.

        Args:
            **kwargs: Parámetros del tool según el input_schema

        Returns:
            Dict con el resultado de la ejecución

        Raises:
            Exception: Si hay un error en la ejecución
        """
        pass
