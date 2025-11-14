from fastapi import APIRouter
from app.api.v1.endpoints import query, health, openrouter, anthropic

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(openrouter.router, prefix="/openrouter", tags=["openrouter"])
api_router.include_router(anthropic.router, prefix="/anthropic", tags=["anthropic"])
