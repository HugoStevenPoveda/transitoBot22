.PHONY: init clean help

init:
	@echo "📁 Creando estructura de carpetas para RAG Backend..."
	@mkdir -p app/api/v1/endpoints
	@mkdir -p app/core
	@mkdir -p app/models
	@mkdir -p app/services
	@mkdir -p app/repositories
	@mkdir -p app/utils
	@mkdir -p app/db
	@mkdir -p tests/test_api
	@mkdir -p tests/test_services
	@mkdir -p tests/test_utils
	@mkdir -p data/documents
	@mkdir -p data/cache
	@mkdir -p scripts
	@touch app/__init__.py
	@touch app/api/__init__.py
	@touch app/api/v1/__init__.py
	@touch app/api/v1/endpoints/__init__.py
	@touch app/core/__init__.py
	@touch app/models/__init__.py
	@touch app/services/__init__.py
	@touch app/repositories/__init__.py
	@touch app/utils/__init__.py
	@touch app/db/__init__.py
	@touch tests/__init__.py
	@echo "# RAG Backend\n\nEstructura de proyecto creada exitosamente." > README.md
	@echo "✅ Estructura creada exitosamente"
	@echo ""
	@echo "📂 Estructura generada:"
	@tree -L 3 -I '__pycache__|*.pyc' . || find . -type d -maxdepth 3 | sed 's|[^/]*/| |g'

create-files:
	@echo "📝 Creando archivos iniciales..."
	
	# __init__.py files
	touch app/__init__.py
	touch app/api/__init__.py
	touch app/api/v1/__init__.py
	touch app/api/v1/endpoints/__init__.py
	touch app/core/__init__.py
	touch app/models/__init__.py
	touch app/services/__init__.py
	touch app/repositories/__init__.py
	touch app/utils/__init__.py
	touch app/db/__init__.py
	touch tests/__init__.py
	
	# Main FastAPI app
	@echo 'from fastapi import FastAPI\nfrom app.api.v1.router import api_router\nfrom app.core.config import settings\n\napp = FastAPI(title=settings.PROJECT_NAME)\n\napp.include_router(api_router, prefix="/api/v1")\n\n@app.get("/")\ndef root():\n    return {"message": "¡Hola Mundo! RAG Backend API"}' > app/main.py
	
	# Config
	@echo 'from pydantic_settings import BaseSettings\n\nclass Settings(BaseSettings):\n    PROJECT_NAME: str = "RAG Backend"\n    VERSION: str = "1.0.0"\n    API_V1_STR: str = "/api/v1"\n    \n    class Config:\n        env_file = ".env"\n\nsettings = Settings()' > app/core/config.py
	
	# Router
	@echo 'from fastapi import APIRouter\nfrom app.api.v1.endpoints import health, chat\n\napi_router = APIRouter()\n\napi_router.include_router(health.router, prefix="/health", tags=["health"])\napi_router.include_router(chat.router, prefix="/chat", tags=["chat"])' > app/api/v1/router.py
	
	# Health endpoint
	@echo 'from fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get("")\ndef health_check():\n    return {"status": "ok", "message": "¡El servidor está funcionando!"}' > app/api/v1/endpoints/health.py
	
	# Chat endpoint
	@echo 'from fastapi import APIRouter\nfrom app.models.chat import ChatRequest, ChatResponse\n\nrouter = APIRouter()\n\n@router.post("", response_model=ChatResponse)\ndef chat(request: ChatRequest):\n    return ChatResponse(\n        response=f"Recibí tu mensaje: {request.message}",\n        sources=[]\n    )' > app/api/v1/endpoints/chat.py
	
	# Chat models
	@echo 'from pydantic import BaseModel\nfrom typing import List\n\nclass ChatRequest(BaseModel):\n    message: str\n    \nclass ChatResponse(BaseModel):\n    response: str\n    sources: List[str] = []' > app/models/chat.py
	
	# Requirements
	@echo 'fastapi==0.115.0\nuvicorn[standard]==0.32.0\npydantic==2.9.2\npydantic-settings==2.6.0\npython-dotenv==1.0.1' > requirements.txt
	
	# .env.example
	@echo 'PROJECT_NAME="RAG Backend"\nVERSION="1.0.0"' > .env.example
	
	# .env
	cp .env.example .env
	
	# .gitignore
	@echo '__pycache__/\n*.py[cod]\n*$$py.class\n*.so\n.Python\nvenv/\nenv/\n.env\n.venv\ndata/\n*.log\n.DS_Store' > .gitignore
	
	# README
	@echo '# RAG Backend\n\n## Instalación\n\n```bash\nmake setup\n```\n\n## Ejecutar\n\n```bash\nmake run\n```\n\n## Endpoints\n\n- GET `/` - Hola Mundo\n- GET `/api/v1/health` - Health check\n- POST `/api/v1/chat` - Chat endpoint' > README.md
	
	@echo "✅ Archivos creados"

install:
	@echo "📦 Instalando dependencias..."
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Dependencias instaladas"

run:
	@echo "🚀 Iniciando servidor..."
	./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	@echo "🧹 Limpiando proyecto..."
	rm -rf venv
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf **/__pycache__
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Proyecto limpio"

test:
	@echo "🧪 Ejecutando tests..."
	./venv/bin/pytest tests/ -v

help:
	@echo "Comandos disponibles:"
	@echo "  make setup  - Crea la estructura completa e instala dependencias"
	@echo "  make run    - Inicia el servidor FastAPI"
	@echo "  make clean  - Limpia archivos temporales"
	@echo "  make test   - Ejecuta los tests"
	@echo "  make help   - Muestra esta ayuda"