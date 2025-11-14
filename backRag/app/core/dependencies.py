import logging
from functools import lru_cache
from typing import Generator
from app.core.config import settings
from app.repositories.chroma_repository import ChromaRepository
from app.services.llm_service import LLMService
from app.services.search_service import SearchService
from app.services.response_service import ResponseService
from app.services.health_service import HealthService
from app.services.openrouter_service import OpenRouterService
from app.services.anthropic_service import AnthropicService

logger = logging.getLogger(__name__)

# Variables globales para instancias singleton
_db_repository: ChromaRepository = None
_llm_service: LLMService = None
_openrouter_service: OpenRouterService = None
_anthropic_service: AnthropicService = None


def get_db_repository() -> ChromaRepository:
    """
    Dependency para obtener el repositorio de ChromaDB.
    Implementa patrón Singleton.
    """
    global _db_repository

    if _db_repository is None:
        logger.info("Inicializando ChromaRepository...")
        _db_repository = ChromaRepository(
            db_path=settings.CHROMA_DB_PATH,
            model_name=settings.EMBEDDING_MODEL
        )
        # Intentar obtener la colección existente
        if not _db_repository.get_collection():
            logger.warning("⚠️ ChromaDB no encontrado. Ejecuta el script de setup primero")

    return _db_repository


def get_llm_service() -> LLMService:
    """
    Dependency para obtener el servicio LLM.
    Implementa patrón Singleton.
    """
    global _llm_service

    if _llm_service is None:
        logger.info("Inicializando LLMService...")
        _llm_service = LLMService(api_key=settings.ANTHROPIC_API_KEY)

    return _llm_service


def get_openrouter_service() -> OpenRouterService:
    """
    Dependency para obtener el servicio OpenRouter.
    Implementa patrón Singleton.
    """
    global _openrouter_service

    if _openrouter_service is None:
        logger.info("Inicializando OpenRouterService...")
        _openrouter_service = OpenRouterService(api_key=settings.OPENROUTER_API_KEY)

    return _openrouter_service


def get_anthropic_service() -> AnthropicService:
    """
    Dependency para obtener el servicio Anthropic.
    Implementa patrón Singleton.
    """
    global _anthropic_service

    if _anthropic_service is None:
        logger.info("Inicializando AnthropicService...")
        _anthropic_service = AnthropicService(api_key=settings.ANTHROPIC_API_KEY)

    return _anthropic_service


def get_search_service(
    db_repository: ChromaRepository = None
) -> SearchService:
    """
    Dependency para obtener el servicio de búsqueda.

    Args:
        db_repository: Repositorio de ChromaDB (inyectado)
    """
    if db_repository is None:
        db_repository = get_db_repository()

    return SearchService(db_manager=db_repository)


def get_response_service(
    llm_service: LLMService = None
) -> ResponseService:
    """
    Dependency para obtener el servicio de respuestas.

    Args:
        llm_service: Servicio LLM (inyectado)
    """
    if llm_service is None:
        llm_service = get_llm_service()

    return ResponseService(llm_service=llm_service)


def get_health_service(
    db_repository: ChromaRepository = None,
    llm_service: LLMService = None
) -> HealthService:
    """
    Dependency para obtener el servicio de health.

    Args:
        db_repository: Repositorio de ChromaDB (inyectado)
        llm_service: Servicio LLM (inyectado)
    """
    if db_repository is None:
        db_repository = get_db_repository()

    if llm_service is None:
        llm_service = get_llm_service()

    return HealthService(
        db_manager=db_repository,
        llm_service=llm_service
    )
