import logging
import time
from fastapi import APIRouter, HTTPException
from app.models import OpenRouterRequest, OpenRouterResponse
from app.core.dependencies import get_openrouter_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=OpenRouterResponse)
async def chat_openrouter(
    request: OpenRouterRequest
):
    """
    Generar respuesta usando OpenRouter con contexto, intención y entidades.

    Este endpoint utiliza OpenRouter para generar respuestas basadas en un contexto
    estructurado, la pregunta del usuario, entidades detectadas y la intención.
    Es útil para casos de uso de NLU donde ya se ha procesado la entrada del usuario.

    El modelo y los parámetros están configurados en el sistema y no se pueden
    modificar por request individual.

    Args:
        request: OpenRouterRequest con los siguientes campos:
            - context: Objeto con contextos del sistema y usuario
                - system: Contexto del sistema para el modelo
                - user: Contexto específico del usuario
            - pregunta: La pregunta o consulta del usuario
            - entidades: Lista de entidades detectadas (puede estar vacía)
            - intencion: Intención clasificada de la consulta

    Returns:
        OpenRouterResponse con:
            - answer: La respuesta generada por el modelo
            - model_used: El modelo que se utilizó (configurado en sistema)
            - processing_time: Tiempo de procesamiento en segundos

    Raises:
        HTTPException 400: Si los campos obligatorios están vacíos
        HTTPException 503: Si el servicio OpenRouter no está disponible
        HTTPException 500: Si hay un error al procesar la solicitud

    Example:
        ```json
        {
            "context": {
                "system": "Eres un asistente experto en tránsito de Colombia",
                "user": "Usuario consultando sobre infracciones"
            },
            "pregunta": "¿Cuál es la multa por exceso de velocidad?",
            "entidades": [{"tipo": "infraccion", "valor": "exceso_velocidad"}],
            "intencion": "consultar_multa"
        }
        ```
    """
    start_time = time.time()

    try:
        # Obtener servicio
        openrouter_service = get_openrouter_service()

        # Verificar disponibilidad
        if not openrouter_service.client:
            raise HTTPException(
                status_code=503,
                detail="Servicio OpenRouter no disponible. Verifica la configuración de OPENROUTER_API_KEY"
            )

        # Validar inputs
        if not request.pregunta or not request.pregunta.strip():
            raise HTTPException(
                status_code=400,
                detail="El campo 'pregunta' no puede estar vacío"
            )

        if not request.context.system or not request.context.system.strip():
            raise HTTPException(
                status_code=400,
                detail="El campo 'context.system' no puede estar vacío"
            )

        if not request.context.user or not request.context.user.strip():
            raise HTTPException(
                status_code=400,
                detail="El campo 'context.user' no puede estar vacío"
            )

        if not request.intencion or not request.intencion.strip():
            raise HTTPException(
                status_code=400,
                detail="El campo 'intencion' no puede estar vacío"
            )

        logger.info(f"📨 Procesando consulta OpenRouter")
        logger.info(f"   Intención: {request.intencion}")
        logger.info(f"   Pregunta: {request.pregunta[:100]}...")

        # Generar respuesta
        answer = openrouter_service.chat_with_context(
            system_context=request.context.system,
            user_context=request.context.user,
            pregunta=request.pregunta,
            entidades=request.entidades,
            intencion=request.intencion
        )

        processing_time = time.time() - start_time

        logger.info(f"✅ Respuesta generada en {processing_time:.2f}s")

        return OpenRouterResponse(
            answer=answer,
            model_used=settings.OPENROUTER_MODEL,
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"❌ Error de validación: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error procesando consulta OpenRouter: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
