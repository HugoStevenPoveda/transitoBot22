"""
Modelos para la comunicación con el cliente (UI)
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class UserMessage(BaseModel):
    """Mensaje enviado por el usuario desde la UI"""
    sender_id: str = Field(..., description="ID único del usuario")
    message: str = Field(..., description="Mensaje del usuario")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata adicional (canal, sesión, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sender_id": "user_12345",
                "message": "Quiero consultar multas",
                "metadata": {
                    "channel": "web",
                    "session_id": "abc123"
                }
            }
        }


class BotMessageItem(BaseModel):
    """Un mensaje individual del bot"""
    text: Optional[str] = Field(None, description="Texto del mensaje")
    image: Optional[str] = Field(None, description="URL de imagen")
    buttons: Optional[List[Dict[str, str]]] = Field(None, description="Botones de acción")
    custom: Optional[Dict[str, Any]] = Field(None, description="Datos personalizados")


class BotResponse(BaseModel):
    """Respuesta completa del bot al usuario"""
    sender_id: str = Field(..., description="ID del usuario")
    messages: List[BotMessageItem] = Field(..., description="Lista de mensajes del bot")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "sender_id": "user_12345",
                "messages": [
                    {
                        "text": "Por favor, proporciona el número de placa del vehículo"
                    }
                ],
                "timestamp": "2025-10-16T10:30:00Z"
            }
        }


class ChatHistoryResponse(BaseModel):
    """Historial de conversación"""
    sender_id: str
    messages: List[Dict[str, Any]]
    total_messages: int
