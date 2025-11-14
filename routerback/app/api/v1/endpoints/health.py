"""
Endpoints de health check
"""
from fastapi import APIRouter, status
from datetime import datetime
import logging

from app.core.rasa_client import rasa_client
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check del orquestador y conexión con RASA
    """
    rasa_connected = await rasa_client.health_check()

    health_status = {
        "status": "healthy" if rasa_connected else "degraded",
        "app_name": settings.app_name,
        "timestamp": datetime.utcnow().isoformat(),
        "rasa": {
            "connected": rasa_connected,
            "url": settings.rasa_url
        }
    }

    if not rasa_connected:
        logger.warning("RASA no está disponible")

    return health_status


@router.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    Endpoint raíz - información básica de la API
    """
    return {
        "message": "RASA Chat Orchestrator API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
