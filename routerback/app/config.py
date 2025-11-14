"""
Configuración de la aplicación
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # FastAPI
    app_name: str = "RASA Chat Orchestrator"
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = True

    # RASA
    rasa_url: str = "http://localhost:5005"
    rasa_webhook_path: str = "/webhooks/rest/webhook"
    rasa_tracker_path: str = "/conversations"
    rasa_timeout: int = 30

    # BackRag (Fallback RAG service)
    backrag_url: str = "http://localhost:8001"
    backrag_query_path: str = "/api/v1/query"
    backrag_timeout: int = 30

    # CORS
    cors_origins: list = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuración
settings = Settings()
