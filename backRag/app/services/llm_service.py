import os
import logging
from typing import List, Dict, Optional
from anthropic import Anthropic
from app.utils.promps import PROMPT_TEMPLATE_QUERY, system_prompt

logger = logging.getLogger(__name__)


class LLMService:
    """Servicio para generar respuestas naturales usando Claude de Anthropic."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio LLM.

        Args:
            api_key: Clave API de Anthropic. Si no se proporciona, se busca en variables de entorno.
        """
        self.historial = []
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY',"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")

        if not self.api_key:
            logger.warning("⚠️ No se encontró ANTHROPIC_API_KEY. Usando respuestas básicas.")
            self.client = None
        else:
            try:
                logger.info("🔑 Inicializando cliente Claude de Anthropic")
                logger.info(self.api_key)
                self.client = Anthropic(api_key='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')
            except Exception as e:
                logger.error(f"❌ Error inicializando Claude: {e}")
                self.client = None
    
    def limpiar_historial(self):
        self.historial = []

    def generar_respuesta_natural(
        self,
        consulta: str,
        articulos_relevantes: List[Dict],
        confianza_promedio: float
    ) -> str:
        """
        Genera una respuesta natural y conversacional basada en los artículos encontrados.

        Args:
            consulta: Pregunta original del usuario
            articulos_relevantes: Lista de artículos encontrados en ChromaDB
            confianza_promedio: Nivel de confianza promedio de la búsqueda

        Returns:
            str: Respuesta natural y conversacional
        """

        # Si no hay Claude disponible, usar respuesta básica mejorada
        if not self.client:
            return self._generar_respuesta_basica(consulta, articulos_relevantes, confianza_promedio)

        # Si no hay artículos relevantes, respuesta amable de limitación
        if not articulos_relevantes or confianza_promedio < 0.3:
            return self._generar_respuesta_sin_resultados(consulta)

        try:
            # Preparar contexto para Claude
            contexto_articulos = self._preparar_contexto_articulos(articulos_relevantes)
            # Prompt optimizado para respuestas sobre tránsito
            prompt = self._construir_prompt(consulta, contexto_articulos, confianza_promedio)
            logger.info(f"✅ PROMP : { prompt})")
            logger.info(f"✅ PROMP : { prompt})")
            
            response = self.client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=300,
                temperature=0.2,
                system=consulta,  
                messages=[
                    *self.historial[-3:],
                    {"role": "user", "content": prompt}
                ]
            )

            respuesta_natural = response.content[0].text.strip()
            # Actualiza historial
            self.historial.append({"role": "user", "content":  prompt})
            self.historial.append({"role": "assistant", "content":  respuesta_natural})
            logger.info(f"////////////////////////  respuesta_natural { respuesta_natural}")
            logger.info(f"✅ Respuesta generada con Claude (confianza: {confianza_promedio:.2f})")

            return respuesta_natural

        except Exception as e:
            logger.error(f"❌ Error generando respuesta con Claude: {e}")
            return self._generar_respuesta_basica(consulta, articulos_relevantes, confianza_promedio)
    
    def _preparar_contexto_articulos(self, articulos: List[Dict]) -> str:
        """Prepara el contexto de artículos para el prompt."""
        contexto = ""

        for i, articulo in enumerate(articulos[:3], 1):
            metadata = articulo['metadata']
            contenido = articulo['documento']
            similitud = articulo['similitud']

            contexto += f"\n--- ARTÍCULO {i} (Relevancia: {similitud:.0%}) ---\n"
            contexto += f"Número: {metadata['numero_articulo']}\n"
            contexto += f"Título: {metadata.get('titulo', 'Sin título')}\n"
            contexto += f"Contenido: {contenido[:500]}...\n"

        return contexto

    def _construir_prompt(self, consulta: str, contexto: str, confianza: float) -> str:
        """Construye el prompt optimizado para Claude."""
        prompt =  PROMPT_TEMPLATE_QUERY.substitute(
            consulta=consulta,
            articulos=contexto)
        return prompt

    
    def _generar_respuesta_sin_resultados(self, consulta: str) -> str:
        """Genera una respuesta amable cuando no se encuentran resultados relevantes."""

        if not self.client:
            return self._respuesta_sin_resultados_basica()

        try:
            prompt = f"""Eres TránsitoBot, un asistente virtual especializado en normas de tránsito de Colombia.

Un usuario preguntó: "{consulta}"

Pero no encontraste información relevante en tu base de datos del Código Nacional de Tránsito.

Responde de manera amable y profesional:
1. Disculpándote por no tener información específica sobre su consulta
2. Explicando que te especializas en temas específicos del código de tránsito
3. Mencionando algunos temas en los que SÍ puedes ayudar (multas, documentos, velocidades, etc.)
4. Sugiriendo que reformule la pregunta si está relacionada con tránsito
5. Mantén un tono amable y servicial

Máximo 150 palabras."""

            response = self.client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=200,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Error generando respuesta sin resultados: {e}")
            return self._respuesta_sin_resultados_basica()

    def _generar_respuesta_basica(self, consulta: str, articulos: List[Dict], confianza: float) -> str:
        """Genera respuesta básica mejorada sin LLM."""

        if not articulos or confianza < 0.3:
            return self._respuesta_sin_resultados_basica()

        # Tomar el artículo más relevante
        articulo_principal = articulos[0]
        metadata = articulo_principal['metadata']
        contenido = articulo_principal['documento']

        # Respuesta básica pero más natural
        respuesta = f"Según el Artículo {metadata['numero_articulo']} del Código Nacional de Tránsito:\n\n"

        # Extraer información relevante
        if len(contenido) > 500:
            parrafos = contenido.split('\n')
            parrafos_relevantes = [p.strip() for p in parrafos[:3] if p.strip()]
            respuesta += '\n'.join(parrafos_relevantes)
        else:
            respuesta += contenido

        # Agregar información adicional si hay más artículos
        if len(articulos) > 1:
            respuesta += f"\n\n📋 **También es importante revisar:**"
            for articulo in articulos[1:3]:
                metadata_adicional = articulo['metadata']
                respuesta += f"\n• Artículo {metadata_adicional['numero_articulo']}"

        respuesta += "\n\n¿Te gustaría que profundice en algún aspecto específico?"

        return respuesta

    def _respuesta_sin_resultados_basica(self) -> str:
        """Respuesta básica cuando no hay resultados."""
        return """Lo siento, no encontré información específica sobre tu consulta en mi base de datos del Código Nacional de Tránsito. 😔

🚦 **Puedo ayudarte con temas como:**
• Multas y sanciones (pico y placa, velocidad, etc.)
• Documentos obligatorios del vehículo
• Límites de velocidad en diferentes zonas
• Normas sobre uso del celular al conducir
• Regulaciones de semáforos y señales
• Parqueo en zona azul

¿Podrías reformular tu pregunta o preguntarme sobre alguno de estos temas? ¡Estoy aquí para ayudarte! 🚗✨"""

    def verificar_disponibilidad(self) -> Dict[str, any]:
        """Verifica si el servicio LLM está disponible."""
        return {
            "claude_disponible": self.client is not None,
            "api_key_configurada": bool(self.api_key),
            "modelo": "claude-3-5-haiku-20241022" if self.client else "respuestas_basicas"
        }
