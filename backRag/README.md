# TránsitoBot API - RAG Backend

API REST para consultas sobre el Código Nacional de Tránsito de Colombia usando RAG (Retrieval-Augmented Generation) con ChromaDB y Claude AI.

## Características

- Búsqueda híbrida (vectorial + keywords) en el código de tránsito
- Generación de respuestas naturales con Claude AI (Anthropic)
- Base de datos vectorial con ChromaDB
- Arquitectura limpia y escalable
- API REST con FastAPI
- Documentación automática con Swagger

## Estructura del Proyecto

```
backRag/
├── app/                          # Aplicación principal
│   ├── api/                      # Endpoints de la API
│   │   └── v1/
│   │       ├── endpoints/        # Definición de endpoints
│   │       │   ├── query.py      # Endpoint de consultas
│   │       │   └── health.py     # Health checks
│   │       └── router.py         # Router principal
│   ├── core/                     # Configuración y dependencias
│   │   ├── config.py             # Settings centralizados
│   │   ├── dependencies.py       # Inyección de dependencias
│   │   └── logging_config.py     # Configuración de logs
│   ├── models/                   # Modelos Pydantic
│   ├── services/                 # Lógica de negocio
│   │   ├── llm_service.py        # Integración con Claude
│   │   ├── search_service.py     # Búsqueda híbrida
│   │   ├── response_service.py   # Generación de respuestas
│   │   └── health_service.py     # Health checks
│   ├── repositories/             # Capa de acceso a datos
│   │   └── chroma_repository.py  # Gestión de ChromaDB
│   ├── utils/                    # Utilidades
│   │   └── constants.py          # Constantes
│   └── main.py                   # Factory de la aplicación
├── data/                         # Datos
│   ├── documents/                # Documentos fuente
│   └── chroma_db/                # Base de datos vectorial
├── scripts/                      # Scripts de utilidades
│   ├── setup_database.py         # Setup inicial de ChromaDB
│   └── transit_processor.py      # Procesador de documentos
├── tests/                        # Tests
├── .env                          # Variables de entorno
├── requirements.txt              # Dependencias
├── run.py                        # Punto de entrada
└── README.md                     # Este archivo
```

## Requisitos

- Python 3.9+
- pip o uv para gestión de dependencias

## Instalación

### 1. Clonar el repositorio o navegar a la carpeta

```bash
cd backRag
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Editar el archivo `.env` y agregar tu API key de Anthropic:

```env
ANTHROPIC_API_KEY=tu_api_key_aqui
```

### 5. Configurar la base de datos

Ejecutar el script de setup para crear la base de datos vectorial:

```bash
python scripts/setup_database.py
```

Este script:
- Procesa el documento del código de tránsito
- Genera embeddings con sentence-transformers
- Almacena todo en ChromaDB

## Uso

### Iniciar el servidor

```bash
python run.py
```

O usar uvicorn directamente:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en:
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc

## Endpoints

### Health Checks

#### GET `/api/v1/health`
Verifica el estado de la API y la base de datos.

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database_status": "connected",
  "total_articles": 450
}
```

#### GET `/api/v1/stats`
Obtiene estadísticas de la base de datos.

#### GET `/api/v1/llm-status`
Verifica el estado del servicio LLM (Claude).

### Consultas

#### POST `/api/v1/query`
Realiza una consulta sobre el código de tránsito.

**Request:**
```json
{
  "query": "¿Cuál es la multa por exceso de velocidad?",
  "max_results": 3,
  "confidence_threshold": 0.4
}
```

**Response:**
```json
{
  "answer": "Según el Código de Tránsito colombiano...",
  "confidence": 0.85,
  "sources": [
    {
      "article": "Artículo 123",
      "law": "Ley 769 de 2002 - Código Nacional de Tránsito Terrestre",
      "description": "Exceso de velocidad",
      "similarity_score": 0.92,
      "content_snippet": "..."
    }
  ],
  "processing_time": 0.45
}
```

## Arquitectura

### Capas de la Aplicación

1. **API Layer** (`app/api/`): Endpoints y routing
2. **Service Layer** (`app/services/`): Lógica de negocio
3. **Repository Layer** (`app/repositories/`): Acceso a datos
4. **Core** (`app/core/`): Configuración y dependencias
5. **Models** (`app/models/`): Modelos de datos (Pydantic)

### Flujo de una Consulta

1. Request llega al endpoint `/api/v1/query`
2. `SearchService` realiza búsqueda híbrida:
   - Búsqueda vectorial con embeddings
   - Búsqueda por keywords con sinónimos
   - Combina y rankea resultados
3. `ResponseService` genera respuesta:
   - Intenta usar Claude AI para respuesta natural
   - Fallback a respuesta básica si LLM falla
4. Formatea fuentes y retorna `QueryResponse`

## Desarrollo

### Agregar nuevos endpoints

1. Crear archivo en `app/api/v1/endpoints/`
2. Definir router con FastAPI
3. Registrar en `app/api/v1/router.py`

### Agregar nuevos servicios

1. Crear archivo en `app/services/`
2. Implementar lógica de negocio
3. Registrar dependency en `app/core/dependencies.py`

## Testing

```bash
pytest tests/ -v
```

## Troubleshooting

### Error: ChromaDB no encontrado

Ejecutar el script de setup:
```bash
python scripts/setup_database.py
```

### Error: API key no configurada

Verificar que `.env` tenga la clave correcta:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

### Error al importar módulos

Asegurarse de estar en el directorio correcto y que el entorno virtual esté activado.

## Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.

## Contacto

Para preguntas o soporte, abrir un issue en el repositorio.
# bacrag
