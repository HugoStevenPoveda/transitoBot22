import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SearchService:
    """Servicio para realizar búsquedas híbridas (vectorial + keywords)."""

    def __init__(self, db_manager):
        """
        Inicializa el servicio de búsqueda.

        Args:
            db_manager: Instancia de ChromaDBManager
        """
        self.db_manager = db_manager
        self.synonyms = self._load_synonyms()

    def _load_synonyms(self) -> Dict[str, List[str]]:
        """Carga el diccionario de sinónimos para búsqueda mejorada."""
        return {
            'velocidad': ['rapidez', 'límite', 'máximo', 'velocidades'],
            'ciudad': ['urbana', 'urbano', 'zona urbana', 'vías urbanas'],
            'multa': ['sanción', 'penalidad', 'infracción'],
            'celular': ['móvil', 'teléfono', 'dispositivo'],
            'pico': ['restricción', 'circulación'],
            'límites': ['velocidades', 'máximas', 'mínimas', 'límite'],
            'carretera': ['vía', 'autopista', 'nacional', 'carreteras'],
            'km': ['kilómetros', 'kilometros'],
            'hora': ['h', '/h']
        }

    def hybrid_search(
        self,
        consulta: str,
        n_resultados: int = 3,
        umbral_confianza: float = 0.5
    ) -> Dict:
        """
        Realiza búsqueda híbrida combinando vectorial y palabras clave.

        Args:
            consulta: Query del usuario
            n_resultados: Número máximo de resultados a retornar
            umbral_confianza: Umbral mínimo de similitud

        Returns:
            Dict con resultados encontrados
        """
        # 1. Búsqueda vectorial con umbral más bajo
        resultados_vectoriales = self.db_manager.buscar_articulos(
            consulta=consulta,
            n_resultados=n_resultados * 2,
            umbral_confianza=max(0.2, umbral_confianza - 0.2)
        )

        # 2. Búsqueda por palabras clave
        resultados_keywords = self._keyword_search(consulta, n_resultados)

        # 3. Combinar y eliminar duplicados
        resultados_combinados = self._merge_results(
            resultados_vectoriales['articulos'],
            resultados_keywords
        )

        # 4. Ordenar por similitud y filtrar
        resultados_finales = sorted(
            resultados_combinados,
            key=lambda x: x['similitud'],
            reverse=True
        )
        resultados_filtrados = [r for r in resultados_finales if r['similitud'] >= umbral_confianza]

        # Si no hay resultados con el umbral, aplicar lógica de fallback
        if not resultados_filtrados and resultados_finales:
            umbral_minimo = 0.2
            resultados_filtrados = [r for r in resultados_finales if r['similitud'] >= umbral_minimo]
            if not resultados_filtrados:
                resultados_filtrados = resultados_finales[:1]

        return {
            'consulta': consulta,
            'total_encontrados': len(resultados_filtrados[:n_resultados]),
            'articulos': resultados_filtrados[:n_resultados],
            'tiempo_busqueda': 0.1
        }

    def _keyword_search(self, consulta: str, n_resultados: int) -> List[Dict]:
        """
        Realiza búsqueda por palabras clave con sinónimos.

        Args:
            consulta: Query del usuario
            n_resultados: Número de resultados

        Returns:
            Lista de artículos encontrados
        """
        palabras_clave = consulta.lower().split()

        # Expandir con sinónimos
        for palabra in palabras_clave.copy():
            if palabra in self.synonyms:
                palabras_clave.extend(self.synonyms[palabra])

        # Obtener todos los documentos
        try:
            todos_docs = self.db_manager.collection.get(include=['documents', 'metadatas'])
        except Exception as e:
            logger.error(f"Error obteniendo documentos: {e}")
            return []

        resultados_keywords = []
        for doc, metadata in zip(todos_docs['documents'], todos_docs['metadatas']):
            doc_lower = doc.lower()
            score = 0

            # Contar coincidencias con pesos
            for palabra in palabras_clave:
                if palabra in doc_lower:
                    # Peso mayor si aparece en el título o al inicio
                    if palabra in doc_lower[:200]:
                        score += 2
                    else:
                        score += 1

            if score > 0:
                similitud_normalizada = min(score / (len(palabras_clave) * 2), 1.0)
                resultados_keywords.append({
                    'documento': doc,
                    'metadata': metadata,
                    'similitud': similitud_normalizada,
                    'tipo': 'keyword',
                    'ranking': 0
                })

        return resultados_keywords

    def _merge_results(
        self,
        resultados_vectoriales: List[Dict],
        resultados_keywords: List[Dict]
    ) -> List[Dict]:
        """
        Combina resultados vectoriales y de keywords eliminando duplicados.

        Args:
            resultados_vectoriales: Resultados de búsqueda vectorial
            resultados_keywords: Resultados de búsqueda por keywords

        Returns:
            Lista combinada sin duplicados
        """
        todos_resultados = resultados_vectoriales + resultados_keywords

        resultados_unicos = {}
        for resultado in todos_resultados:
            numero = resultado['metadata']['numero_articulo']
            if numero not in resultados_unicos or resultado['similitud'] > resultados_unicos[numero]['similitud']:
                resultados_unicos[numero] = resultado

        return list(resultados_unicos.values())
