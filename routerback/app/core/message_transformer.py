"""
Transformador de mensajes entre UI y RASA
"""
from typing import List, Dict, Any
from datetime import datetime
import logging

from app.models.chat import UserMessage, BotResponse, BotMessageItem
from app.models.rasa import RasaRequest, RasaResponseItem

logger = logging.getLogger(__name__)


class MessageTransformer:
    """Transforma mensajes entre formatos UI y RASA"""

    @staticmethod
    def ui_to_rasa(user_message: UserMessage) -> RasaRequest:
        """
        Transforma mensaje de UI a formato RASA

        Args:
            user_message: Mensaje del usuario desde la UI

        Returns:
            Request para RASA
        """
        return RasaRequest(
            sender=user_message.sender_id,
            message=user_message.message,
            metadata=user_message.metadata
        )

    @staticmethod
    def rasa_to_ui(
        sender_id: str,
        rasa_responses: List[RasaResponseItem]
    ) -> BotResponse:
        """
        Transforma respuestas de RASA a formato UI

        Args:
            sender_id: ID del usuario
            rasa_responses: Lista de respuestas de RASA

        Returns:
            Respuesta formateada para la UI
        """
        messages = []

        for rasa_item in rasa_responses:
            bot_message = BotMessageItem(
                text=rasa_item.text,
                image=rasa_item.image,
                buttons=rasa_item.buttons,
                custom=rasa_item.custom
            )
            messages.append(bot_message)

        return BotResponse(
            sender_id=sender_id,
            messages=messages,
            timestamp=datetime.utcnow()
        )

    @staticmethod
    def rag_to_ui(
        sender_id: str,
        rag_response: Dict[str, Any]
    ) -> BotResponse:
        """
        Transforma respuesta de BackRag a formato UI

        Args:
            sender_id: ID del usuario
            rag_response: Respuesta del servicio BackRag (QueryResponse)

        Returns:
            Respuesta formateada para la UI
        """
        logger.info(f"[Transformer] Transformando respuesta RAG para sender_id={sender_id}")

        # Extraer la respuesta principal
        answer = rag_response.get("answer", "Lo siento, no pude procesar tu consulta.")
        confidence = rag_response.get("confidence", 0.0)
        sources = rag_response.get("sources", [])

        logger.debug(
            f"[Transformer] RAG Answer: '{answer[:100]}...', "
            f"Confidence: {confidence:.2f}, "
            f"Sources: {len(sources)}"
        )

        # Crear mensaje principal con la respuesta
        main_message = BotMessageItem(
            text=answer,
            custom={
                "source": "backrag",
                "confidence": confidence,
                "sources_count": len(sources)
            }
        )

        messages = [main_message]

        # Si hay fuentes, agregar como metadata adicional (opcional)
        if sources:
            sources_info = []
            for idx, source in enumerate(sources[:3], 1):  # Máximo 3 fuentes
                sources_info.append(
                    f"{idx}. {source.get('article', 'N/A')} - {source.get('law', 'N/A')}"
                )

            logger.debug(f"[Transformer] Fuentes incluidas: {sources_info}")

            # Opcional: Agregar mensaje con fuentes
            if sources_info:
                sources_message = BotMessageItem(
                    text=f"📚 Fuentes consultadas:\n" + "\n".join(sources_info),
                    custom={"type": "sources"}
                )
                messages.append(sources_message)

        logger.info(f"[Transformer] Respuesta RAG transformada: {len(messages)} mensaje(s)")

        return BotResponse(
            sender_id=sender_id,
            messages=messages,
            timestamp=datetime.utcnow()
        )


# Instancia global
message_transformer = MessageTransformer()
