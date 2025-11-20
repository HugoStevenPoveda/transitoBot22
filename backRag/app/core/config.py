from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configuración centralizada de la aplicación."""

    # Base dir absoluto del proyecto
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

    # Información del proyecto
    PROJECT_NAME: str = "TránsitoBot API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para consultas sobre el Código Nacional de Tránsito de Colombia"
    API_V1_STR: str = "/api/v1"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080"
    ]

    # ChromaDB
    CHROMA_DB_PATH: str = os.path.join(BASE_DIR, "data", "chroma_db")
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    COLLECTION_NAME: str = "codigo_transito_colombia"

    # LLM (Anthropic Claude)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "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")
    CLAUDE_MODEL: str = "claude-haiku-4-5"
    CLAUDE_MAX_TOKENS: int =2000
    CLAUDE_TEMPERATURE: float = 0.0

    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "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")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "openai/gpt-oss-20b:free"
    OPENROUTER_MAX_TOKENS: int = 500
    OPENROUTER_TEMPERATURE: float = 0.1

    # Búsqueda
    DEFAULT_MAX_RESULTS: int = 3
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.4
    MIN_CONFIDENCE_THRESHOLD: float = 0.2

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global
settings = Settings()
