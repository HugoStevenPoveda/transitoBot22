"""
Endpoints para chat
"""
from fastapi import APIRouter, HTTPException, status
import logging

from app.models.chat import UserMessage, BotResponse
from app.core.rasa_client import rasa_client
from app.core.backrag_client import backrag_client
from app.core.message_transformer import message_transformer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/message", response_model=BotResponse, status_code=status.HTTP_200_OK)
async def send_message(user_message: UserMessage):
    """
    Envía un mensaje al bot y obtiene la respuesta

    Flujo de fallback:
    1. Intenta primero con RASA
    2. Si RASA no puede responder (lista vacía), usa BackRag como fallback

    - **sender_id**: ID único del usuario
    - **message**: Mensaje del usuario
    - **metadata**: Metadata adicional (opcional)
    """
    try:
        logger.info(f"========== NUEVO MENSAJE ==========")
        logger.info(f"[Chat] Recibido de sender_id={user_message.sender_id}: '{user_message.message}'")

        # PASO 1: Intentar primero con RASA
        logger.info(f"[Chat] PASO 1: Enviando mensaje a RASA...")
        rasa_responses = await rasa_client.send_message(
            sender_id=user_message.sender_id,
            message=user_message.message,
            metadata=user_message.metadata
        )
        logger.info(f"========== RASA RESPONDE ==========")
        logger.info(rasa_responses)
        logger.info(f"[Chat] Respuestas recibidas de RASA: {len(rasa_responses) if rasa_responses else 0}")
        logger.info(f"===================================")
        # PASO 2: Evaluar si RASA pudo responder
        should_use_rag = False
        fallback_reason = None

        if rasa_responses and len(rasa_responses) > 0:
            logger.info(f"[Chat] ✓ RASA respondió con {len(rasa_responses)} mensaje(s)")
            logger.debug(f"[Chat] Respuestas RASA: {rasa_responses}")

            # Evaluar criterios de fallback más inteligentes
            first_response = rasa_responses[0]

            # Criterio 1: Mensaje vacío o solo espacios
            if not first_response.text or first_response.text.strip() == "":
                should_use_rag = True
                fallback_reason = "empty_text"
                logger.info(f"[Chat] Criterio 1: Texto vacío detectado")

            # Criterio 2: Custom metadata indica fallback
            elif first_response.custom and first_response.custom.get("fallback") == True:
                should_use_rag = True
                fallback_reason = first_response.custom.get("reason", "custom_fallback")
                logger.info(f"[Chat] Criterio 2: Metadata de fallback detectada - Razón: {fallback_reason}")

            # Criterio 3: Confianza baja en custom metadata
            elif first_response.custom and first_response.custom.get("confidence", 1.0) < 0.6:
                should_use_rag = True
                confidence = first_response.custom.get("confidence", 0)
                fallback_reason = f"low_confidence_{confidence:.2f}"
                logger.info(f"[Chat] Criterio 3: Baja confianza detectada ({confidence:.2f})")

            # Criterio 4: Intent específico que debe ir a RAG
            elif first_response.custom:
                intent = first_response.custom.get("intent", "")
                if intent in ["out_of_scope", "consulta_codigo_transito", "nlu_fallback"]:
                    should_use_rag = True
                    fallback_reason = f"intent_{intent}"
                    logger.info(f"[Chat] Criterio 4: Intent {intent} debe usar RAG")

            # Si NO debe usar RAG, retornar respuesta de RASA
            if not should_use_rag:
                logger.info(f"[Chat] ✓ RASA manejó la consulta exitosamente")
                bot_response = message_transformer.rasa_to_ui(
                    sender_id=user_message.sender_id,
                    rasa_responses=rasa_responses
                )
                logger.info(f"[Chat] Respuesta final enviada (origen: RASA) - {len(bot_response.messages)} mensaje(s)")
                logger.info(f"========== FIN PROCESAMIENTO ==========")
                return bot_response
            else:
                logger.warning(f"[Chat] ✗ RASA activó fallback - Razón: {fallback_reason}")
        else:
            # RASA no respondió nada
            should_use_rag = True
            fallback_reason = "empty_response_list"
            logger.warning(f"[Chat] ✗ RASA no respondió (lista vacía)")

        # PASO 3: Activar fallback a BackRag
        logger.info(f"[Chat] PASO 3: Activando fallback a BackRag (Razón: {fallback_reason})...")

        rag_response = await backrag_client.query(
            message=user_message.message
        )

        # PASO 4: Evaluar respuesta de BackRag
        if rag_response:
            logger.info(f"[Chat] ✓ BackRag respondió exitosamente")
            logger.debug(f"[Chat] Respuesta BackRag: confidence={rag_response.get('confidence', 0):.2f}")

            bot_response = message_transformer.rag_to_ui(
                sender_id=user_message.sender_id,
                rag_response=rag_response
            )

            logger.info(f"[Chat] Respuesta final enviada (origen: BackRag) - {len(bot_response.messages)} mensaje(s)")
            return bot_response

        # PASO 5: Ni RASA ni BackRag pudieron responder
        logger.error(f"[Chat] ✗ Ni RASA ni BackRag pudieron responder")
        logger.info(f"[Chat] Enviando respuesta genérica de fallback")

        # Respuesta genérica cuando ambos servicios fallan
        from app.models.chat import BotMessageItem
        from datetime import datetime

        fallback_response = BotResponse(
            sender_id=user_message.sender_id,
            messages=[
                BotMessageItem(
                    text="Lo siento, en este momento no puedo procesar tu consulta. Por favor, intenta de nuevo más tarde.",
                    custom={"source": "fallback_error"}
                )
            ],
            timestamp=datetime.utcnow()
        )

        logger.info(f"[Chat] Respuesta genérica enviada")
        logger.info(f"========== FIN PROCESAMIENTO ==========")
        return fallback_response

    except Exception as e:
        logger.error(f"[Chat] ✗✗✗ Error crítico al procesar mensaje: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar mensaje: {str(e)}"
        )


@router.post("/reset/{sender_id}", status_code=status.HTTP_200_OK)
async def reset_conversation(sender_id: str):
    """
    Reinicia la conversación de un usuario

    - **sender_id**: ID del usuario
    """
    try:
        logger.info(f"Reiniciando conversación para: {sender_id}")

        success = await rasa_client.reset_tracker(sender_id)

        if success:
            return {
                "message": f"Conversación reiniciada para {sender_id}",
                "sender_id": sender_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo reiniciar la conversación"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al reiniciar conversación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reiniciar conversación: {str(e)}"
        )


@router.get("/tracker/{sender_id}", status_code=status.HTTP_200_OK)
async def get_conversation_tracker(sender_id: str):
    """
    Obtiene el estado de la conversación de un usuario

    - **sender_id**: ID del usuario
    """
    try:
        logger.info(f"Obteniendo tracker para: {sender_id}")

        tracker = await rasa_client.get_tracker(sender_id)

        if tracker:
            return tracker
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró tracker para {sender_id}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener tracker: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tracker: {str(e)}"
        )
