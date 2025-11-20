from .base_tool import BaseTool
from .search_tool import HybridSearchTool
from .email_tool import EmailSenderTool

# Registro de todas las tools disponibles
AVAILABLE_TOOLS = {
    "buscar_articulos_transito": HybridSearchTool,
    "enviar_email": EmailSenderTool
}

__all__ = ["BaseTool", "HybridSearchTool", "EmailSenderTool", "AVAILABLE_TOOLS"]
