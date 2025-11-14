import logging
from typing import Dict, Optional
from app.models import HealthResponse

logger = logging.getLogger(__name__)


class HealthService:
    """Servicio para health checks y monitoreo del sistema."""

    def __init__(self, db_manager, llm_service):
        """
        Inicializa el servicio de health.

        Args:
            db_manager: Instancia de ChromaDBManager
            llm_service: Instancia de LLMService
        """
        self.db_manager = db_manager
        self.llm_service = llm_service

    def check_health(self) -> HealthResponse:
        """
        Verifica el estado de la API y la base de datos.

        Returns:
            HealthResponse con el estado del sistema
        """
        try:
            if self.db_manager and self.db_manager.collection:
                stats = self.db_manager.obtener_estadisticas_db()
                return HealthResponse(
                    status="healthy",
                    version="1.0.0",
                    database_status="connected",
                    total_articles=stats.get('total_articulos', 0)
                )
            else:
                return HealthResponse(
                    status="degraded",
                    version="1.0.0",
                    database_status="disconnected"
                )
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return HealthResponse(
                status="unhealthy",
                version="1.0.0",
                database_status="error"
            )

    def get_database_stats(self) -> Dict:
        """
        Obtiene estadísticas de la base de datos.

        Returns:
            Diccionario con estadísticas
        """
        if not self.db_manager:
            raise ValueError("Base de datos no disponible")

        return self.db_manager.obtener_estadisticas_db()

    def get_llm_status(self) -> Dict:
        """
        Verifica el estado del servicio LLM (Claude).

        Returns:
            Diccionario con el estado del LLM
        """
        try:
            status = self.llm_service.verificar_disponibilidad()
            return {
                "llm_service": "Claude (Anthropic)",
                "status": "available" if status["claude_disponible"] else "unavailable",
                "api_key_configured": status["api_key_configurada"],
                "model": status["modelo"],
                "ready_for_natural_responses": status["claude_disponible"]
            }
        except Exception as e:
            logger.error(f"Error verificando estado LLM: {e}")
            return {
                "llm_service": "Claude (Anthropic)",
                "status": "error",
                "error": str(e),
                "ready_for_natural_responses": False
            }
