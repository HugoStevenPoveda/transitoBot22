import logging
from typing import Dict, Any
from .base_tool import BaseTool

logger = logging.getLogger(__name__)


class HybridSearchTool(BaseTool):
    """
    Tool para realizar búsqueda híbrida (vectorial + keywords) en el Código Nacional de Tránsito.
    """

    def __init__(self, search_service):
        """
        Inicializa el tool con el servicio de búsqueda.

        Args:
            search_service: Instancia de SearchService
        """
        self.search_service = search_service

    @property
    def name(self) -> str:
        return "buscar_articulos_transito"

    @property
    def description(self) -> str:
        return (
            "Busca artículos relevantes en el Código Nacional de Tránsito de Colombia usando búsqueda semántica híbrida (vectorial + keywords). "
            "Usa esta herramienta cuando el usuario pregunte sobre:\n"
            "- Normas y regulaciones de tránsito\n"
            "- Multas y sanciones\n"
            "- Límites de velocidad\n"
            "- Documentos obligatorios del vehículo\n"
            "- Infracciones y penalidades\n"
            "- Pico y placa\n"
            "- Uso del celular al conducir\n"
            "- Semáforos y señales de tránsito\n"
            "- Cualquier tema relacionado con el código de tránsito terrestre colombiano"
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
                    "consulta": {
                        "type": "string",
                        "description": (
                            "La pregunta o términos de búsqueda sobre el código de tránsito. "
                            "Puede ser una pregunta completa del usuario o palabras clave específicas. "
                            "Ejemplos: 'multa por exceso de velocidad', 'límite de velocidad en zona urbana', 'documentos obligatorios'"
                        )
                    },
                    "n_resultados": {
                        "type": "integer",
                        "description": "Número de artículos a retornar. Por defecto 3. Máximo recomendado: 5",
                        "default": 3
                    },
                    "umbral_confianza": {
                        "type": "number",
                        "description": "Umbral mínimo de similitud semántica (0.0 a 1.0). Por defecto 0.4. Valores más bajos retornan más resultados pero menos precisos",
                        "default": 0.4
                    }
                },
                "required": ["consulta"]
            }
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la búsqueda híbrida en ChromaDB.

        Args:
            consulta (str): Query de búsqueda
            n_resultados (int, optional): Número de resultados. Default: 3
            umbral_confianza (float, optional): Umbral de similitud. Default: 0.4

        Returns:
            Dict con estructura:
            {
                "success": bool,
                "total_encontrados": int,
                "articulos": [
                    {
                        "numero_articulo": str,
                        "titulo": str,
                        "contenido": str,
                        "similitud": float
                    }
                ],
                "mensaje": str (opcional)
            }
        """
        try:
            # Extraer parámetros
            consulta = kwargs.get("consulta")
            n_resultados = kwargs.get("n_resultados", 3)
            umbral_confianza = kwargs.get("umbral_confianza", 0.4)

            if not consulta:
                return {
                    "success": False,
                    "total_encontrados": 0,
                    "articulos": [],
                    "mensaje": "El parámetro 'consulta' es obligatorio"
                }

            logger.info(f"🔍 Ejecutando búsqueda híbrida: '{consulta}' (n={n_resultados}, umbral={umbral_confianza})")

            # Ejecutar búsqueda híbrida
            resultados = self.search_service.hybrid_search(
                consulta=consulta,
                n_resultados=n_resultados,
                umbral_confianza=umbral_confianza
            )

            # Formatear resultados
            articulos_formateados = []
            for articulo in resultados.get("articulos", []):
                articulos_formateados.append({
                    "numero_articulo": articulo["metadata"]["numero_articulo"],
                    "titulo": articulo["metadata"].get("titulo", "Sin título"),
                    "contenido": articulo["documento"],
                    "similitud": round(articulo["similitud"], 3)
                })

            total = len(articulos_formateados)

            logger.info(f"✅ Búsqueda completada: {total} artículos encontrados")

            result = {
                "success": True,
                "total_encontrados": total,
                "articulos": articulos_formateados
            }

            # Agregar mensaje informativo si no se encontraron resultados
            if total == 0:
                result["mensaje"] = (
                    "No se encontraron artículos relevantes con el umbral de confianza especificado. "
                    "Intenta reformular la consulta o reducir el umbral de confianza."
                )

            return result

        except Exception as e:
            logger.error(f"❌ Error ejecutando búsqueda híbrida: {e}")
            return {
                "success": False,
                "total_encontrados": 0,
                "articulos": [],
                "mensaje": f"Error al ejecutar la búsqueda: {str(e)}"
            }
