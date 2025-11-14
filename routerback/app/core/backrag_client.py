"""
Cliente HTTP para comunicarse con BackRag (servicio RAG de fallback)
"""
import httpx
from typing import Optional, Dict, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class BackRagClient:
    """Cliente para comunicarse con el servicio BackRag"""

    def __init__(self):
        self.base_url = settings.backrag_url
        self.query_url = f"{self.base_url}{settings.backrag_query_path}"
        self.timeout = settings.backrag_timeout
        logger.info(f"BackRagClient inicializado - URL: {self.query_url}, Timeout: {self.timeout}s")

    async def query(
        self,
        message: str,
        max_results: int = 3,
        confidence_threshold: float = 0.4
    ) -> Optional[Dict[str, Any]]:
        """
        Envía una consulta a BackRag y obtiene la respuesta RAG

        Args:
            message: Mensaje/pregunta del usuario
            max_results: Número máximo de resultados a buscar
            confidence_threshold: Umbral de confianza para resultados

        Returns:
            Respuesta de BackRag en formato dict o None si hay error
        """
        try:
            logger.info(f"========== INICIA PETICON A RAG==========")
            # Preparar request
            backrag_request = {
                "query": message,
                "max_results": max_results,
                "confidence_threshold": confidence_threshold
            }

            logger.info(f"[BackRag] Enviando consulta: '{message[:50]}...' (max_results={max_results}, threshold={confidence_threshold})")

            # Realizar petición HTTP a BackRag
            logger.info("TIMEE ============00")
            logger.info(self.timeout)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.query_url,
                    json=backrag_request
                )
                response.raise_for_status()

                # Parsear respuesta
                backrag_response = response.json()

                logger.info(
                    f"[BackRag] Respuesta recibida - "
                    f"Confianza: {backrag_response.get('confidence', 0):.2f}, "
                    f"Fuentes: {len(backrag_response.get('sources', []))}, "
                    f"Tiempo: {backrag_response.get('processing_time', 0):.3f}s"
                )
                logger.debug(f"[BackRag] Respuesta completa: {backrag_response}")

                return backrag_response

        except httpx.TimeoutException as e:
            logger.error(f"[BackRag] Timeout al comunicarse con BackRag después de {self.timeout}s: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"[BackRag] Error HTTP {e.response.status_code} al comunicarse con BackRag: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"[BackRag] Error de conexión al comunicarse con BackRag: {e}")
            return None
        except Exception as e:
            logger.error(f"[BackRag] Error inesperado en BackRagClient: {e}", exc_info=True)
            return None

    async def health_check(self) -> bool:
        """
        Verifica si BackRag está disponible

        Returns:
            True si BackRag responde correctamente
        """
        try:
            health_endpoint = f"{self.base_url}/api/v1/health"

            logger.debug(f"[BackRag] Verificando salud del servicio: {health_endpoint}")

            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(health_endpoint)
                response.raise_for_status()

                logger.info(f"[BackRag] Servicio disponible - Status: {response.status_code}")
                return True

        except Exception as e:
            logger.warning(f"[BackRag] Servicio no disponible: {e}")
            return False


# Instancia global del cliente
backrag_client = BackRagClient()
