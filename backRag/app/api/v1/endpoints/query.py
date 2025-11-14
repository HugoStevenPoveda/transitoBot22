import logging
import time
from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse
from app.core.dependencies import get_search_service, get_response_service, get_db_repository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query_transit_bot(
    request: QueryRequest
):
    """
    Procesar consulta sobre normas de tránsito usando búsqueda vectorial y LLM.

    Args:
        request: QueryRequest con la consulta del usuario

    Returns:
        QueryResponse con la respuesta generada
    """
    start_time = time.time()

    try:
        # Obtener servicios
        db_repository = get_db_repository()
        search_service = get_search_service(db_repository)
        response_service = get_response_service()

        if not db_repository or not db_repository.collection:
            raise HTTPException(
                status_code=503,
                detail="Base de datos no disponible. Ejecuta el script de setup primero"
            )

        # Realizar búsqueda híbrida
        resultados = search_service.hybrid_search(
            consulta=request.query,
            n_resultados=request.max_results,
            umbral_confianza=request.confidence_threshold
        )

        if not resultados['articulos']:
            # Si no hay resultados, devolver respuesta genérica
            return QueryResponse(
                answer="Lo siento, no encontré información específica sobre tu consulta en el código de tránsito. ¿Podrías reformular tu pregunta?",
                confidence=0.0,
                sources=[],
                processing_time=time.time() - start_time
            )

        # Calcular confianza promedio
        confianza_promedio = response_service.calculate_confidence(resultados['articulos'])

        # Generar respuesta (con LLM o fallback)
        respuesta = response_service.generate_response(
            consulta=request.query,
            articulos=resultados['articulos'],
            confianza_promedio=confianza_promedio
        )

        # Convertir artículos a formato de fuentes
        sources = response_service.format_sources(resultados['articulos'])
        logger.info("Consulta procesada exitosamente")
        logger.info(respuesta)
        return QueryResponse(
            answer=respuesta,
            confidence=confianza_promedio,
            sources=sources,
            processing_time=time.time() - start_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando consulta: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
