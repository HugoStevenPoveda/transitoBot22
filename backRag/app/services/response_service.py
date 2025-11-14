import logging
from typing import List, Dict
from app.models import Source

logger = logging.getLogger(__name__)


class ResponseService:
    """Servicio para generar y formatear respuestas."""

    def __init__(self, llm_service):
        """
        Inicializa el servicio de respuestas.

        Args:
            llm_service: Instancia de LLMService
        """
        self.llm_service = llm_service

    def generate_response(
        self,
        consulta: str,
        articulos: List[Dict],
        confianza_promedio: float
    ) -> str:
        """
        Genera respuesta usando LLM o respuesta básica como fallback.

        Args:
            consulta: Pregunta del usuario
            articulos: Artículos relevantes encontrados
            confianza_promedio: Nivel de confianza promedio

        Returns:
            Respuesta generada
        """
        if not articulos:
            return "Lo siento, no encontré información específica sobre tu consulta en el código de tránsito. ¿Podrías reformular tu pregunta?"

        # Generar respuesta básica primero
        #respuesta_basica = self._generar_respuesta_contextual(consulta, articulos)
        respuesta_basica = "mensaje de prueba"

        # Intentar mejorar con LLM
        try:
            respuesta_llm = self.llm_service.generar_respuesta_natural(
                consulta=consulta,
                articulos_relevantes=articulos,
                confianza_promedio=confianza_promedio
            )

            # Si LLM genera respuesta más completa, usarla
            if respuesta_llm and len(respuesta_llm) > len(respuesta_basica):
                logger.info("✅ Respuesta generada con Claude LLM")
                return respuesta_llm

        except Exception as e:
            logger.warning(f"⚠️ LLM falló, usando respuesta básica: {e}")

        return respuesta_basica

    def _generar_respuesta_contextual(self, consulta: str, articulos: List[Dict]) -> str:
        """
        Genera una respuesta contextual básica basada en los artículos encontrados.

        Args:
            consulta: Pregunta del usuario
            articulos: Artículos encontrados

        Returns:
            Respuesta contextual
        """
        if not articulos:
            return "No se encontró información relevante en el código de tránsito."

        # Tomar el artículo más relevante
        articulo_principal = articulos[0]
        metadata = articulo_principal['metadata']
        contenido = articulo_principal['documento']

        # Generar respuesta básica
        respuesta = f"Según el Artículo {metadata['numero_articulo']} del Código Nacional de Tránsito:\n\n"

        # Extraer información relevante del contenido
        if len(contenido) > 500:
            # Si es muy largo, tomar los primeros párrafos más relevantes
            parrafos = contenido.split('\n')
            parrafos_relevantes = [p for p in parrafos[:3] if p.strip()]
            respuesta += '\n'.join(parrafos_relevantes)
        else:
            respuesta += contenido

        # Agregar información adicional si hay más artículos relevantes
        if len(articulos) > 1:
            respuesta += f"\n\nTambién es relevante revisar:"
            for i, articulo in enumerate(articulos[1:3], 2):
                metadata_adicional = articulo['metadata']
                respuesta += f"\n• Artículo {metadata_adicional['numero_articulo']}"

        return respuesta

    def format_sources(self, articulos: List[Dict]) -> List[Source]:
        """
        Convierte artículos a formato de fuentes para la respuesta.

        Args:
            articulos: Lista de artículos encontrados

        Returns:
            Lista de objetos Source
        """
        sources = []
        for articulo in articulos:
            metadata = articulo['metadata']
            source = Source(
                article=f"Artículo {metadata['numero_articulo']}",
                law="Ley 769 de 2002 - Código Nacional de Tránsito Terrestre",
                description=metadata.get('titulo', 'Código Nacional de Tránsito'),
                similarity_score=articulo['similitud'],
                content_snippet=articulo['documento'][:300] + "..." if len(articulo['documento']) > 300 else articulo['documento']
            )
            sources.append(source)

        return sources

    def calculate_confidence(self, articulos: List[Dict]) -> float:
        """
        Calcula confianza promedio basada en los artículos.

        Args:
            articulos: Lista de artículos con similitud

        Returns:
            Confianza promedio
        """
        if not articulos:
            return 0.0

        return sum(a['similitud'] for a in articulos) / len(articulos)
