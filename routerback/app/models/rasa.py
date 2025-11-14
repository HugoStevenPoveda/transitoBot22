"""
Modelos para la comunicación con RASA
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class RasaRequest(BaseModel):
    """Request que se envía a RASA"""
    sender: str = Field(..., description="ID del sender/usuario")
    message: str = Field(..., description="Mensaje del usuario")
    metadata: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "sender": "user_12345",
                "message": "Quiero consultar multas"
            }
        }


class RasaResponseItem(BaseModel):
    """Un item de respuesta de RASA"""
    recipient_id: str
    text: Optional[str] = None
    image: Optional[str] = None
    buttons: Optional[List[Dict[str, str]]] = None
    custom: Optional[Dict[str, Any]] = None


class RasaTrackerEvent(BaseModel):
    """Evento en el tracker de RASA"""
    event: str
    timestamp: Optional[float] = None
    name: Optional[str] = None
    value: Optional[Any] = None
    text: Optional[str] = None


class RasaTrackerResponse(BaseModel):
    """Respuesta del tracker de RASA"""
    sender_id: str
    slots: Dict[str, Any]
    latest_message: Optional[Dict[str, Any]] = None
    events: List[Dict[str, Any]]
    paused: bool
    followup_action: Optional[str] = None
