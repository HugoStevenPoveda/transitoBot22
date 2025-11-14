import os
import logging
from typing import Dict, Optional, List
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterService:
    """Servicio para generar respuestas usando OpenRouter."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio OpenRouter.

        Args:
            api_key: Clave API de OpenRouter. Si no se proporciona, se busca en variables de entorno.
        """
        self.api_key = api_key or settings.OPENROUTER_API_KEY

        if not self.api_key:
            logger.warning("⚠️ No se encontró OPENROUTER_API_KEY. El servicio no estará disponible.")
            self.client = None
        else:
            try:
                logger.info("🔑 Inicializando cliente OpenRouter")
                self.client = openai.OpenAI(
                    base_url=settings.OPENROUTER_BASE_URL,
                    api_key=self.api_key
                )
                logger.info(f"✅ Cliente OpenRouter inicializado con modelo: {settings.OPENROUTER_MODEL}")
            except Exception as e:
                logger.error(f"❌ Error inicializando OpenRouter: {e}")
                self.client = None

    def chat_with_context(
        self,
        system_context: str,
        user_context: str,
        pregunta: str,
        entidades: List[dict],
        intencion: str
    ) -> str:
        """
        Genera una respuesta basada en el contexto, pregunta, entidades e intención.

        Args:
            system_context: Contexto del sistema para el modelo
            user_context: Contexto específico del usuario
            pregunta: Pregunta del usuario
            entidades: Lista de entidades detectadas
            intencion: Intención de la consulta

        Returns:
            str: Respuesta generada por el modelo

        Raises:
            ValueError: Si el servicio no está disponible
            Exception: Si hay un error en la generación
        """
        if not self.client:
            raise ValueError("El servicio OpenRouter no está disponible. Verifica la configuración de la API key.")

        try:
            logger.info(f"📤 Enviando consulta a OpenRouter")
            logger.info(f"   system_context: {system_context}")
            logger.info(f"   user_context: {user_context}")
            logger.info(f"   Intención: {intencion}")
            logger.info(f"   Pregunta: {pregunta[:100]}...")
            logger.info(f"   Entidades: {len(entidades)} detectadas")

            # Construir mensaje del sistema completo
            system_message = f"{system_context}\n\nContexto del usuario: {user_context}"

            # Construir mensaje del usuario con metadatos
            user_message = f"Pregunta: {pregunta}\n"
            if entidades:
                user_message += f"Entidades detectadas: {entidades}\n"
            user_message += f"Intención: {intencion}"

            response = self.client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=settings.OPENROUTER_MAX_TOKENS,
                temperature=settings.OPENROUTER_TEMPERATURE
            )

            answer = response.choices[0].message.content
            logger.info(f"✅ Respuesta generada exitosamente: {answer}")
            logger.info(f"✅ Respuesta generada exitosamente: {len(answer)} caracteres")

            return answer

        except Exception as e:
            logger.error(f"❌ Error generando respuesta con OpenRouter: {e}")
            raise Exception(f"Error al procesar la solicitud: {str(e)}")

    def verificar_disponibilidad(self) -> Dict[str, any]:
        """
        Verifica si el servicio OpenRouter está disponible.

        Returns:
            Dict con información sobre la disponibilidad del servicio
        """
        return {
            "openrouter_disponible": self.client is not None,
            "api_key_configurada": bool(self.api_key),
            "modelo": settings.OPENROUTER_MODEL if self.client else "no_disponible",
            "base_url": settings.OPENROUTER_BASE_URL
        }
