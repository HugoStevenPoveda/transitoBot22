import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.dependencies import get_db_repository
from app.api.v1.router import api_router

# Configurar logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    # Startup
    logger.info("🚀 Iniciando TránsitoBot API...")

    # Inicializar ChromaDB
    try:
        db_repository = get_db_repository()
        if db_repository.get_collection():
            logger.info("✅ ChromaDB conectado exitosamente")
        else:
            logger.warning("⚠️ ChromaDB no encontrado. Ejecuta el script de setup primero")
    except Exception as e:
        logger.error(f"❌ Error conectando ChromaDB: {e}")

    yield  # Aquí la aplicación está corriendo

    # Shutdown
    logger.info("🔄 Cerrando aplicación...")


def create_app() -> FastAPI:
    """
    Factory para crear la aplicación FastAPI.

    Returns:
        Instancia configurada de FastAPI
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        lifespan=lifespan
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Incluir routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Endpoint root
    @app.get("/")
    async def root():
        """Endpoint raíz con información básica."""
        return {
            "message": "TránsitoBot API - Código Nacional de Tránsito de Colombia",
            "version": settings.VERSION,
            "docs": "/docs",
            "health": f"{settings.API_V1_STR}/health"
        }

    logger.info(f"✅ Aplicación '{settings.PROJECT_NAME}' configurada exitosamente")

    return app


# Crear instancia de la aplicación
app = create_app()
