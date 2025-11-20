from .base_tool import BaseTool
from .search_tool import HybridSearchTool

# Registro de todas las tools disponibles
AVAILABLE_TOOLS = {
    "buscar_articulos_transito": HybridSearchTool
}

__all__ = ["BaseTool", "HybridSearchTool", "AVAILABLE_TOOLS"]
