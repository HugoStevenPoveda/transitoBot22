#!/usr/bin/env python3
"""
Script para configurar la base de datos ChromaDB con el código de tránsito.
"""
import os
import sys

# Agregar el directorio padre al path para poder importar app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.repositories.chroma_repository import ChromaRepository
from scripts.transit_processor import ProcesadorCodigoTransito
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Ruta base del proyecto (sube desde scripts/ al directorio raíz)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Función principal para configurar ChromaDB."""

    # Configurar ChromaDB
    logger.info("Inicializando ChromaRepository...")
    # Inicializar repositorio con ruta correcta
    db_path = os.path.join(BASE_DIR, "data", "chroma_db")
    db_repository = ChromaRepository(db_path=db_path)

    # Crear colección (recrear=True para empezar limpio)
    if not db_repository.create_collection(recreate=True):
        logger.error("❌ Error creando colección")
        return

    # Procesar y almacenar el código de tránsito
    archivo_codigo = os.path.join(BASE_DIR, "data", "documents", "CodigoNacionaldeTransitoTerrestre.docx")

    logger.info(f"Procesando archivo: {archivo_codigo}")

    if not os.path.exists(archivo_codigo):
        raise FileNotFoundError(f"❌ No se encontró el archivo: {archivo_codigo}")

    if not os.path.exists(archivo_codigo):
        logger.error(f"❌ Archivo '{archivo_codigo}' no encontrado")
        logger.info("Asegúrate de tener el archivo en la carpeta data/documents/")
        return

    logger.info("Procesando código de tránsito...")
    procesador = ProcesadorCodigoTransito()
    articulos = procesador.procesar_codigo_transito(archivo_codigo)

    if not articulos:
        logger.error("No se pudieron procesar artículos")
        return

    logger.info(f"Procesados {len(articulos)} artículos")

    # Preparar documentos para vectorización
    documentos = procesador.exportar_para_vectorizacion()

    # Asegurar IDs únicos
    ids_vistos = set()
    documentos_unicos = []

    for i, doc in enumerate(documentos):
        id_original = doc['id']
        if id_original in ids_vistos:
            doc['id'] = f"{id_original}_{i}"
        ids_vistos.add(doc['id'])
        documentos_unicos.append(doc)

    documentos = documentos_unicos

    # Extraer datos
    textos = [doc['texto'] for doc in documentos]
    ids = [doc['id'] for doc in documentos]

    # Limpiar metadatos - ChromaDB no acepta valores None
    metadatos = []
    for doc in documentos:
        metadata_limpio = {}
        for key, value in doc['metadata'].items():
            if value is not None:
                if isinstance(value, bool):
                    metadata_limpio[key] = str(value)
                else:
                    metadata_limpio[key] = value
            else:
                metadata_limpio[key] = ""
        metadatos.append(metadata_limpio)

    # Almacenar en ChromaDB
    if db_repository.add_documents(textos, metadatos, ids):
        logger.info("✅ Base de datos creada exitosamente!")

        # Mostrar estadísticas
        stats = db_repository.get_stats()
        logger.info("\n=== ESTADÍSTICAS DE LA BASE DE DATOS ===")
        for key, value in stats.items():
            logger.info(f"{key}: {value}")

        # Hacer una búsqueda de prueba
        logger.info("\n=== PRUEBA DE BÚSQUEDA ===")
        resultados = db_repository.search_articles("¿Cuál es la multa por pico y placa?", umbral_confianza=0.1)

        logger.info(f"Consulta: {resultados['consulta']}")
        logger.info(f"Artículos encontrados: {resultados['total_encontrados']}")

        for articulo in resultados['articulos'][:3]:
            logger.info(f"\n--- Artículo {articulo['metadata']['numero_articulo']} ---")
            logger.info(f"Similitud: {articulo['similitud']:.2%}")
            logger.info(f"Contenido: {articulo['documento'][:200]}...")

    else:
        logger.error("❌ Error procesando el código de tránsito")


if __name__ == "__main__":
    main()
