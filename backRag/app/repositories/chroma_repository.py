import chromadb
import os
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ChromaRepository:
    """Repositorio para gestionar ChromaDB local con el código de tránsito."""

    def __init__(
        self,
        db_path: str = "./data/chroma_db",
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Inicializa el repositorio de ChromaDB.

        Args:
            db_path: Ruta donde se guardará la base de datos local
            model_name: Modelo de embeddings a usar
        """
        self.db_path = db_path
        self.model_name = model_name

        # Crear directorio si no existe
        os.makedirs(db_path, exist_ok=True)

        # Inicializar ChromaDB (persistente en disco)
        self.client = chromadb.PersistentClient(path=db_path)

        # Cargar modelo de embeddings
        logger.info(f"Cargando modelo de embeddings: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)

        # Nombre de la colección
        self.collection_name = "codigo_transito_colombia"
        self.collection = None

    def get_collection(self) -> bool:
        """
        Obtiene la colección existente.

        Returns:
            True si la colección existe, False en caso contrario
        """
        try:
            self.collection = self.client.get_collection(self.collection_name)
            return True
        except Exception as e:
            logger.warning(f"Colección '{self.collection_name}' no existe: {e}")
            return False

    def create_collection(self, recreate: bool = False) -> bool:
        """
        Crea la colección en ChromaDB.

        Args:
            recreate: Si True, elimina la colección existente y crea una nueva

        Returns:
            True si se creó correctamente, False en caso contrario
        """
        try:
            if recreate:
                try:
                    self.client.delete_collection(self.collection_name)
                    logger.info(f"Colección '{self.collection_name}' eliminada")
                except Exception:
                    pass

            # Crear colección con función de embedding personalizada
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=None,
                metadata={
                    "description": "Código Nacional de Tránsito Terrestre de Colombia",
                    "hnsw:space": "cosine"
                }
            )

            logger.info(f"Colección '{self.collection_name}' creada exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error creando colección: {e}")
            return False

    def search_articles(
        self,
        consulta: str,
        n_resultados: int = 3,
        umbral_confianza: float = 0.7
    ) -> Dict:
        """
        Busca artículos relevantes usando búsqueda vectorial.

        Args:
            consulta: Pregunta del usuario
            n_resultados: Número máximo de resultados
            umbral_confianza: Umbral mínimo de similitud

        Returns:
            Diccionario con resultados de la búsqueda
        """
        logger.info(f"Buscando: '{consulta}'")

        # Generar embedding de la consulta
        query_embedding = self.embedding_model.encode([consulta]).tolist()

        # Buscar en ChromaDB
        resultados = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_resultados * 2,
            include=['documents', 'metadatas', 'distances']
        )

        # Procesar resultados
        articulos_encontrados = []

        for i, (documento, metadata, distancia) in enumerate(zip(
            resultados['documents'][0],
            resultados['metadatas'][0],
            resultados['distances'][0]
        )):
            # Similitud Coseno: 1 - distancia
            similitud = 1 - distancia

            if similitud >= umbral_confianza:
                articulo = {
                    'documento': documento,
                    'metadata': metadata,
                    'similitud': similitud,
                    'ranking': i + 1
                }
                articulos_encontrados.append(articulo)

        # Limitar a n_resultados
        articulos_encontrados = articulos_encontrados[:n_resultados]

        logger.info(f"Encontrados {len(articulos_encontrados)} artículos relevantes")

        return {
            'consulta': consulta,
            'total_encontrados': len(articulos_encontrados),
            'articulos': articulos_encontrados,
            'tiempo_busqueda': 0.1
        }

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de la base de datos.

        Returns:
            Diccionario con estadísticas
        """
        try:
            count = self.collection.count()
            return {
                'total_articulos': count,
                'coleccion': self.collection_name,
                'modelo_embeddings': self.model_name,
                'ruta_db': self.db_path
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ) -> bool:
        """
        Añade documentos a la colección.

        Args:
            documents: Lista de textos de documentos
            metadatas: Lista de metadatos
            ids: Lista de IDs únicos

        Returns:
            True si se añadieron correctamente
        """
        try:
            logger.info("Generando embeddings...")
            embeddings = self.embedding_model.encode(
                documents,
                show_progress_bar=True,
                batch_size=32
            ).tolist()

            logger.info("Almacenando en ChromaDB...")
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"✅ {len(documents)} documentos almacenados exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error añadiendo documentos: {e}")
            return False

    # Métodos legacy para compatibilidad (alias)
    def obtener_coleccion(self) -> bool:
        """Alias para get_collection (compatibilidad)."""
        return self.get_collection()

    def buscar_articulos(self, consulta: str, n_resultados: int = 3, umbral_confianza: float = 0.7) -> Dict:
        """Alias para search_articles (compatibilidad)."""
        return self.search_articles(consulta, n_resultados, umbral_confianza)

    def obtener_estadisticas_db(self) -> Dict:
        """Alias para get_stats (compatibilidad)."""
        return self.get_stats()
