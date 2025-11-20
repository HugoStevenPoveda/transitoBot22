import os
import logging
import json
from typing import Dict, Optional, List, Any
from anthropic import Anthropic
from app.core.config import settings

logger = logging.getLogger(__name__)


class AnthropicService:
    """Servicio para generar respuestas usando Anthropic Claude."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio Anthropic.

        Args:
            api_key: Clave API de Anthropic. Si no se proporciona, se busca en variables de entorno.
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY

        if not self.api_key:
            logger.warning("⚠️ No se encontró ANTHROPIC_API_KEY. El servicio no estará disponible.")
            self.client = None
        else:
            try:
                logger.info("🔑 Inicializando cliente Anthropic")
                self.client = Anthropic(api_key='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')
                logger.info(f"✅ Cliente Anthropic inicializado con modelo: {settings.CLAUDE_MODEL}")
            except Exception as e:
                logger.error(f"❌ Error inicializando Anthropic: {e}")
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
            raise ValueError("El servicio Anthropic no está disponible. Verifica la configuración de la API key.")

        try:
            logger.info(f"📤 Enviando consulta a Anthropic Claude")
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

            response = self.client.messages.create(
                model='claude-haiku-4-5',
                max_tokens=settings.CLAUDE_MAX_TOKENS,
                temperature=settings.CLAUDE_TEMPERATURE,
                system=system_message,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            answer = response.content[0].text
            logger.info(f"✅ Respuesta generada exitosamente: {answer}")
            logger.info(f"✅ Respuesta generada exitosamente: {len(answer)} caracteres")

            return answer

        except Exception as e:
            logger.error(f"❌ Error generando respuesta con Anthropic: {e}")
            raise Exception(f"Error al procesar la solicitud: {str(e)}")

    def verificar_disponibilidad(self) -> Dict[str, any]:
        """
        Verifica si el servicio Anthropic está disponible.

        Returns:
            Dict con información sobre la disponibilidad del servicio
        """
        return {
            "anthropic_disponible": self.client is not None,
            "api_key_configurada": bool(self.api_key),
            "modelo": settings.CLAUDE_MODEL if self.client else "no_disponible"
        }

    def chat_with_tools(
        self,
        system_context: str,
        user_context: str,
        pregunta: str,
        entidades: List[dict],
        intencion: str,
        tools: List[Dict[str, Any]],
        tool_manager,
        max_iterations: int = 5
    ) -> str:
        """
        Genera una respuesta usando Claude con function calling (tools).

        Implementa un loop agentic donde Claude puede usar herramientas para
        obtener información antes de generar la respuesta final.

        Args:
            system_context: Contexto del sistema para el modelo
            user_context: Contexto específico del usuario
            pregunta: Pregunta del usuario
            entidades: Lista de entidades detectadas
            intencion: Intención de la consulta
            tools: Lista de definiciones de tools en formato Anthropic
            tool_manager: Instancia de ToolManager para ejecutar tools
            max_iterations: Número máximo de iteraciones del loop. Default: 5

        Returns:
            str: Respuesta generada por el modelo

        Raises:
            ValueError: Si el servicio no está disponible
            Exception: Si hay un error en la generación
        """
        if not self.client:
            raise ValueError("El servicio Anthropic no está disponible. Verifica la configuración de la API key.")

        try:
            logger.info(f"🔧 Iniciando chat con tools habilitados")
            logger.info(f"   Tools disponibles: {[tool['name'] for tool in tools]}")
            logger.info(f"   Intención: {intencion}")
            logger.info(f"   Pregunta: {pregunta[:100]}...")

            # Construir mensaje del sistema completo
            system_message = f"Genera un correo profesional de máximo 150 tokens. No excedas ese límite \n\n {system_context}\n\nContexto del usuario: {user_context}"
            logger.info("///////"*50)
            logger.info(f"     system_message : {  system_message }...")
            logger.info("///////"*50)
            # Construir mensaje del usuario con metadatos
            user_message = f"Pregunta: {pregunta}\n"
            if entidades:
                user_message += f"Entidades detectadas: {entidades}\n"
            user_message += f"Intención: {intencion}"

            # Inicializar conversación
            messages = [{"role": "user", "content": user_message}]

            # Loop agentic
            for iteration in range(max_iterations):
                logger.info(f"🔄 Iteración {iteration + 1}/{max_iterations}")

                # Llamar a Claude con tools habilitados
                response = self.client.messages.create(
                    model='claude-haiku-4-5',
                    max_tokens=settings.CLAUDE_MAX_TOKENS,
                    temperature=settings.CLAUDE_TEMPERATURE,
                    system=system_message,
                    messages=messages,
                    tools=tools
                )

                logger.info(f"📥 Stop reason: {response.stop_reason}")

                # Procesar respuesta según stop_reason
                if response.stop_reason == "end_turn":
                    # Claude terminó sin usar tools
                    # Buscar el texto en los content blocks
                    text_response = ""
                    for block in response.content:
                        if hasattr(block, 'type') and block.type == "text":
                            text_response = block.text
                            break

                    logger.info(f"✅ Respuesta final generada sin tools (iteración {iteration + 1})")
                    return text_response

                elif response.stop_reason == "tool_use":
                    # Claude quiere usar uno o más tools
                    logger.info(f"🔧 Claude solicita usar tool(s)")

                    # Agregar respuesta de Claude a messages
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    # Procesar cada tool_use en la respuesta
                    tool_results = []
                    for block in response.content:
                        if hasattr(block, 'type') and block.type == "tool_use":
                            tool_name = block.name
                            tool_input = block.input
                            tool_use_id = block.id

                            logger.info(f"   🔨 Tool: {tool_name}")
                            logger.info(f"   📝 Input: {tool_input}")

                            # Ejecutar tool
                            try:
                                tool_result = tool_manager.execute_tool(
                                    tool_name=tool_name,
                                    tool_input=tool_input
                                )
                                logger.info(f"   ✅ Tool ejecutado exitosamente")

                            except Exception as e:
                                logger.error(f"   ❌ Error ejecutando tool: {e}")
                                tool_result = {
                                    "success": False,
                                    "error": str(e)
                                }

                            # Agregar resultado a la lista
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps(tool_result, ensure_ascii=False)
                            })

                    # Agregar tool_results a messages
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })

                    # Continuar al siguiente iteration

                elif response.stop_reason == "max_tokens":
                    logger.warning(f"⚠️ Se alcanzó el límite de tokens")
                    # Intentar extraer texto de la respuesta
                    text_response = ""
                    for block in response.content:
                        if hasattr(block, 'type') and block.type == "text":
                            text_response = block.text
                            break

                    if text_response:
                        return text_response
                    else:
                        return "Lo siento, la respuesta fue muy larga. Por favor, intenta con una pregunta más específica."

                else:
                    logger.warning(f"⚠️ Stop reason inesperado: {response.stop_reason}")
                    break

            # Si se alcanzó max_iterations sin respuesta final
            logger.warning(f"⚠️ Se alcanzó el máximo de iteraciones ({max_iterations})")
            return "Lo siento, no pude procesar tu consulta completamente. Por favor, intenta reformularla."

        except Exception as e:
            logger.error(f"❌ Error generando respuesta con tools: {e}")
            raise Exception(f"Error al procesar la solicitud con tools: {str(e)}")
