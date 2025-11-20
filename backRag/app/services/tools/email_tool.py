import logging
import os
from typing import Dict, Any
from .base_tool import BaseTool
import requests

logger = logging.getLogger(__name__)


class EmailSenderTool(BaseTool):
    """
    Tool para enviar correos electrónicos a través del servicio de email externo.
    """

    def __init__(self, email_service_url: str = None):
        """
        Inicializa el tool con la URL del servicio de email.

        Args:
            email_service_url: URL del servicio de envío de emails.
                             Si no se proporciona, se obtiene de EMAIL_SERVICE_URL env var.
        """
        if email_service_url is None:
            email_service_url = os.getenv(
                "EMAIL_SERVICE_URL",
                "http://appchat-apistool:8076/api/v1/email/send"
            )
        self.email_service_url = email_service_url

    @property
    def name(self) -> str:
        return "enviar_email"

    @property
    def description(self) -> str:
        return (
            "Envía un correo electrónico a la dirección especificada. "
            "Usa esta herramienta cuando el usuario solicite:\n"
            "- Enviar notificaciones por correo\n"
            "- Enviar alertas importantes\n"
            "- Enviar confirmaciones\n"
            "- Enviar resúmenes de información\n"
            "- Enviar cualquier tipo de comunicación por email\n"
            "IMPORTANTE: Esta herramienta envía emails reales. Úsala solo cuando el usuario lo solicite explícitamente."
        )

    def get_definition(self) -> Dict[str, Any]:
        """
        Retorna la definición del tool en formato Anthropic API.
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "to_email": {
                        "type": "string",
                        "description": (
                            "Dirección de correo electrónico del destinatario. "
                            "Debe ser un email válido (ejemplo: usuario@dominio.com)"
                        )
                    },
                    "motivo": {
                        "type": "string",
                        "description": (
                            "Asunto o motivo del correo electrónico. "
                            "Descripción breve del propósito del email (ejemplo: 'Notificación importante', 'Resumen de consulta')"
                        )
                    },
                    "mensaje": {
                        "type": "string",
                        "description": (
                            "Contenido del mensaje del correo electrónico. "
                            "Texto completo que se enviará en el cuerpo del email"
                        )
                    }
                },
                "required": ["to_email", "motivo", "mensaje"]
            }
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta el envío de email a través del servicio externo.

        Args:
            to_email (str): Dirección de email del destinatario
            motivo (str): Asunto del correo
            mensaje (str): Contenido del mensaje

        Returns:
            Dict con estructura:
            {
                "success": bool,
                "mensaje": str,
                "to_email": str,
                "detalle": str (opcional)
            }
        """
        try:
            # Extraer parámetros
            to_email = kwargs.get("to_email")
            motivo = kwargs.get("motivo")
            mensaje = kwargs.get("mensaje")

            # Validar parámetros obligatorios
            if not to_email:
                return {
                    "success": False,
                    "mensaje": "El parámetro 'to_email' es obligatorio",
                    "to_email": ""
                }

            if not motivo:
                return {
                    "success": False,
                    "mensaje": "El parámetro 'motivo' es obligatorio",
                    "to_email": to_email
                }

            if not mensaje:
                return {
                    "success": False,
                    "mensaje": "El parámetro 'mensaje' es obligatorio",
                    "to_email": to_email
                }

            logger.info(f"📧 Enviando email a '{to_email}' con motivo: '{motivo}'")

            # Preparar payload
            payload = {
                "to_email": to_email,
                "motivo": motivo,
                "mensaje": mensaje
            }

            # Realizar llamada HTTP POST al servicio de email
            response = requests.post(
                self.email_service_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )

            # Procesar respuesta
            if response.status_code == 200:
                response_data = response.json()

                logger.info(f"✅ Email enviado exitosamente a '{to_email}'")

                return {
                    "success": response_data.get("success", True),
                    "mensaje": response_data.get("message", "Email enviado exitosamente"),
                    "to_email": response_data.get("to_email", to_email)
                }
            else:
                # Error del servicio
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", error_data.get("message", ""))
                except:
                    error_detail = response.text

                logger.error(f"❌ Error del servicio de email (status {response.status_code}): {error_detail}")

                return {
                    "success": False,
                    "mensaje": f"Error al enviar email: {error_detail}",
                    "to_email": to_email,
                    "detalle": f"Status code: {response.status_code}"
                }

        except requests.ConnectionError as e:
            logger.error(f"❌ No se pudo conectar al servicio de email: {e}")
            return {
                "success": False,
                "mensaje": "El servicio de email no está disponible. Verifica que el servicio esté corriendo en http://0.0.0.0:8076",
                "to_email": kwargs.get("to_email", ""),
                "detalle": str(e)
            }

        except requests.Timeout as e:
            logger.error(f"❌ Timeout al conectar con el servicio de email: {e}")
            return {
                "success": False,
                "mensaje": "El servicio de email no respondió a tiempo. Intenta nuevamente",
                "to_email": kwargs.get("to_email", ""),
                "detalle": "Timeout después de 10 segundos"
            }

        except Exception as e:
            logger.error(f"❌ Error inesperado al enviar email: {e}")
            return {
                "success": False,
                "mensaje": f"Error inesperado al enviar email: {str(e)}",
                "to_email": kwargs.get("to_email", ""),
                "detalle": str(type(e).__name__)
            }
