"""
Cliente HTTP para comunicarse con RASA
"""
import httpx
from typing import List, Optional, Dict, Any
import logging

from app.config import settings
from app.models.rasa import RasaRequest, RasaResponseItem, RasaTrackerResponse

logger = logging.getLogger(__name__)


class RasaClient:
    """Cliente para comunicarse con el servidor RASA"""

    def __init__(self):
        self.base_url = settings.rasa_url
        self.webhook_url = f"{self.base_url}{settings.rasa_webhook_path}"
        self.tracker_url = f"{self.base_url}{settings.rasa_tracker_path}"
        self.timeout = settings.rasa_timeout

    async def send_message(
        self,
        sender_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[RasaResponseItem]:
        """
        Envía un mensaje a RASA y obtiene la respuesta

        Args:
            sender_id: ID único del usuario
            message: Mensaje del usuario
            metadata: Metadata adicional

        Returns:
            Lista de respuestas de RASA
        """
        try:
            # Preparar request
            rasa_request = RasaRequest(
                sender=sender_id,
                message=message,
                metadata=metadata or {}
            )

            logger.info(f"Enviando mensaje a RASA: sender={sender_id}, message={message}")

            # Realizar petición HTTP a RASA
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=rasa_request.model_dump()
                )
                response.raise_for_status()

                # Parsear respuesta
                rasa_responses = response.json()
                logger.info(f"Respuesta de RASA: {len(rasa_responses)} mensajes")

                # Convertir a modelos Pydantic
                return [
                    RasaResponseItem(**item)
                    for item in rasa_responses
                ]

        except httpx.HTTPError as e:
            logger.error(f"Error HTTP al comunicarse con RASA: {e}")
            raise Exception(f"Error al comunicarse con RASA: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado en RasaClient: {e}")
            raise

    async def get_tracker(self, sender_id: str) -> Optional[RasaTrackerResponse]:
        """
        Obtiene el tracker (estado de conversación) de un usuario

        Args:
            sender_id: ID del usuario

        Returns:
            Tracker de RASA o None si hay error
        """
        try:
            tracker_endpoint = f"{self.tracker_url}/{sender_id}/tracker"

            logger.info(f"Obteniendo tracker para: {sender_id}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(tracker_endpoint)
                response.raise_for_status()

                tracker_data = response.json()
                return RasaTrackerResponse(**tracker_data)

        except httpx.HTTPError as e:
            logger.error(f"Error al obtener tracker: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener tracker: {e}")
            return None

    async def reset_tracker(self, sender_id: str) -> bool:
        """
        Reinicia la conversación de un usuario

        Args:
            sender_id: ID del usuario

        Returns:
            True si se reinició exitosamente
        """
        try:
            tracker_endpoint = f"{self.tracker_url}/{sender_id}/tracker/events"

            logger.info(f"Reiniciando conversación para: {sender_id}")

            # Evento para reiniciar
            reset_event = {
                "event": "restart"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    tracker_endpoint,
                    json=reset_event
                )
                response.raise_for_status()

                logger.info(f"Conversación reiniciada para: {sender_id}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Error al reiniciar conversación: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al reiniciar conversación: {e}")
            return False

    async def health_check(self) -> bool:
        """
        Verifica si RASA está disponible

        Returns:
            True si RASA responde correctamente
        """
        try:
            health_endpoint = f"{self.base_url}/status"

            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(health_endpoint)
                response.raise_for_status()
                return True

        except Exception as e:
            logger.error(f"RASA no está disponible: {e}")
            return False


# Instancia global del cliente
rasa_client = RasaClient()
