import logging
from fastapi import APIRouter, HTTPException
from app.models import HealthResponse
from app.core.dependencies import get_health_service, get_openrouter_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health_check():
    """Verificar el estado de la API y la base de datos."""
    health_service = get_health_service()
    return health_service.check_health()


@router.get("/stats")
async def get_database_stats():
    """Obtener estadísticas de la base de datos."""
    try:
        health_service = get_health_service()
        return health_service.get_database_stats()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/llm-status")
async def get_llm_status():
    """Verificar el estado del servicio LLM (Claude)."""
    health_service = get_health_service()
    return health_service.get_llm_status()


@router.get("/openrouter-status")
async def get_openrouter_status():
    """Verificar el estado del servicio OpenRouter."""
    try:
        openrouter_service = get_openrouter_service()
        status = openrouter_service.verificar_disponibilidad()
        return {
            "status": "available" if status["openrouter_disponible"] else "unavailable",
            **status
        }
    except Exception as e:
        logger.error(f"Error verificando estado de OpenRouter: {e}")
        raise HTTPException(status_code=500, detail=str(e))
