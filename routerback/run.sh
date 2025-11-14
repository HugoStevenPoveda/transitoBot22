#!/bin/bash

# Script para iniciar el orquestador FastAPI

echo "======================================"
echo "  RASA Chat Orchestrator"
echo "======================================"
echo ""

# Activar entorno virtual
if [ -d ".venv" ]; then
    echo "Activando entorno virtual..."
    source .venv/bin/activate
else
    echo "Error: No se encontró el entorno virtual (.venv)"
    echo "Ejecuta: uv venv && uv pip install -r requirements.txt"
    exit 1
fi

# Verificar dependencias
echo "Verificando dependencias..."
python -c "import fastapi, uvicorn, httpx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Dependencias no instaladas"
    echo "Ejecuta: uv pip install -r requirements.txt"
    exit 1
fi

# Iniciar servidor
echo ""
echo "Iniciando servidor FastAPI..."
echo "Documentación: http://localhost:8000/docs"
echo "Health check: http://localhost:8000/api/v1/health"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
