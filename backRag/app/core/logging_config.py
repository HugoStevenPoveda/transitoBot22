import logging
import sys
from app.core.config import settings


def setup_logging():
    """Configura el sistema de logging de la aplicación."""

    # Formato de logs
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configurar logging básico
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Configurar loggers específicos
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configurado - Nivel: {settings.LOG_LEVEL}")

    return logger
