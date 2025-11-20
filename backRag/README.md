# BackRag - Sistema RAG con ChromaDB y Claude AI

Sistema de Retrieval-Augmented Generation (RAG) para consultas sobre el Código Nacional de Tránsito de Colombia. Combina búsqueda vectorial, ChromaDB y Claude AI (Anthropic) con **function calling** para generar respuestas precisas y contextuales.

## Rol en el Sistema Transibot

BackRag es el cerebro del sistema Transibot, proporcionando:

- **Búsqueda Inteligente**: Búsqueda híbrida (vectorial + keywords) en el código de tránsito
- **Generación de Respuestas**: Usa Claude AI para respuestas naturales y contextuales
- **Function Calling**: Permite a Claude usar herramientas (búsqueda, envío de emails)
- **Base de Conocimiento**: ChromaDB con embeddings de artículos del código de tránsito

### Integración con otros servicios

```
┌──────────────┐
│ RouterBack   │ ──────> Envía consultas del usuario
│ (Port 8080)  │
└──────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│          BackRag (Port 8000)          │
│                                       │
│  ┌─────────────────────────────────┐ │
│  │   Anthropic Service (Claude)    │ │
│  │   + Function Calling Tools      │ │
│  └──────────┬──────────────────────┘ │
│             │                         │
│    ┌────────┴────────┐               │
│    │                 │               │
│    ▼                 ▼               │
│  ┌──────────┐  ┌─────────────┐      │
│  │ Search   │  │Email Sender │      │
│  │  Tool    │  │    Tool     │──┐   │
│  └────┬─────┘  └─────────────┘  │   │
│       │                          │   │
│       ▼                          │   │
│  ┌──────────┐                   │   │
│  │ChromaDB  │                   │   │
│  │(Vectors) │                   │   │
│  └──────────┘                   │   │
└─────────────────────────────────┼───┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │   ApiTool    │
                          │ (Port 8076)  │
                          └──────────────┘
```

## Arquitectura del Servicio

### Arquitectura RAG Completa

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Application                 │
│                    (app/main.py)                     │
└──────────────────────┬──────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│   API Router    │         │     Models      │
│   (v1/router)   │         │   (Pydantic)    │
└────────┬────────┘         └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│            Services Layer (Lógica)                   │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  Anthropic   │  │    Search    │  │   Tool   │  │
│  │   Service    │  │   Service    │  │ Manager  │  │
│  │              │  │              │  │          │  │
│  │ • Claude API │  │ • Búsqueda   │  │ • Search │  │
│  │ • Function   │  │   híbrida    │  │   Tool   │  │
│  │   Calling    │  │ • Vectorial  │  │ • Email  │  │
│  │ • Tools      │  │ • Keywords   │  │   Tool   │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
│                                                      │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│          Repository Layer (Data Access)              │
│                                                      │
│           ┌──────────────────────────┐              │
│           │  ChromaDB Repository     │              │
│           │                          │              │
│           │ • Vector search          │              │
│           │ • Metadata filtering     │              │
│           │ • Collection management  │              │
│           └──────────────────────────┘              │
│                       │                              │
└───────────────────────┼──────────────────────────────┘
                        │
                        ▼
                ┌──────────────┐
                │   ChromaDB   │
                │ (Persistent  │
                │   Storage)   │
                └──────────────┘
```

### Flujo de una Consulta con Function Calling

```
1. Request HTTP POST → /api/v1/query
   {
     "query": "¿Cuál es la multa por exceso de velocidad y envíame la info a mi email?"
   }

2. RouterBack recibe y envía a BackRag
   └─> POST http://backrag:8000/api/v1/query

3. AnthropicService (Claude AI)
   └─> Analiza la consulta
   └─> Detecta necesidad de usar tools:
       • buscar_articulos_transito (para buscar info)
       • enviar_email (para enviar resultados)

4. ToolManager ejecuta tools
   a) buscar_articulos_transito
      └─> SearchService.hybrid_search()
          └─> ChromaDB búsqueda vectorial
          └─> Búsqueda por keywords + sinónimos
          └─> Combina y rankea resultados
          └─> Retorna artículos relevantes

   b) enviar_email (si el usuario lo solicita)
      └─> EmailSenderTool
          └─> HTTP POST a ApiTool
          └─> ApiTool envía email vía SMTP

5. Claude genera respuesta natural
   └─> Usa resultados de las tools
   └─> Formatea respuesta contextual
   └─> Incluye fuentes (artículos del código)

6. Response al usuario
   └─> {
         "answer": "Respuesta natural de Claude...",
         "confidence": 0.92,
         "sources": [...],
         "processing_time": 1.2
       }
```

## Estructura de Implementación

```
backRag/
├── app/
│   ├── __init__.py
│   ├── main.py                          # ⭐ Aplicación FastAPI
│   │
│   ├── api/                             # Capa API
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── query.py             # ⭐ Endpoint de consultas RAG
│   │       │   └── health.py            # Health checks
│   │       └── router.py                # Router agregador v1
│   │
│   ├── core/                            # Configuración
│   │   ├── config.py                    # ⭐ Settings (env vars)
│   │   ├── dependencies.py              # Inyección de dependencias
│   │   └── logging_config.py            # Logs
│   │
│   ├── models/                          # Schemas Pydantic
│   │   ├── query.py                     # QueryRequest, QueryResponse
│   │   └── health.py                    # HealthResponse
│   │
│   ├── services/                        # Lógica de negocio
│   │   ├── anthropic_service.py         # ⭐ Claude AI + Function Calling
│   │   ├── search_service.py            # ⭐ Búsqueda híbrida
│   │   ├── tool_manager.py              # ⭐ Gestión de tools
│   │   ├── health_service.py            # Health checks
│   │   └── tools/                       # ⭐ Tools para function calling
│   │       ├── base_tool.py             # Clase base para tools
│   │       ├── search_tool.py           # Tool de búsqueda
│   │       └── email_tool.py            # Tool de envío de email
│   │
│   ├── repositories/                    # Acceso a datos
│   │   └── chroma_repository.py         # ⭐ Gestión de ChromaDB
│   │
│   └── utils/
│       └── constants.py                 # Constantes
│
├── data/                                # ⭐ Datos persistentes
│   ├── documents/                       # Documentos fuente (PDF, TXT)
│   └── chroma_db/                       # Base de datos vectorial
│
├── scripts/                             # Scripts de utilidad
│   ├── setup_database.py                # ⭐ Setup inicial ChromaDB
│   └── transit_processor.py             # Procesador de documentos
│
├── tests/                               # Tests unitarios
│
├── Dockerfile                           # ⭐ Multi-stage build
├── requirements.txt                     # ⭐ Dependencias
├── pyproject.toml                       # Configuración del proyecto
├── docker-entrypoint.sh                 # Entrypoint script
├── run.py                               # Punto de entrada local
└── README.md
```

## Elementos Importantes del Servicio

### 1. **Anthropic Service** (`anthropic_service.py`)

Servicio principal para interactuar con Claude AI:

**Características:**
- ✅ Integración con API de Anthropic
- ✅ **Function Calling**: Claude puede usar tools dinámicamente
- ✅ Manejo de contexto (system + user)
- ✅ Soporte para entidades e intenciones
- ✅ Streaming de respuestas (opcional)
- ✅ Fallback si API falla

**Método principal:**
```python
def chat_with_context(
    system_context: str,
    user_context: str,
    pregunta: str,
    entidades: List[dict],
    intencion: str
) -> str
```

**Tools disponibles para Claude:**
1. `buscar_articulos_transito`: Busca en el código de tránsito
2. `enviar_email`: Envía información por correo

### 2. **Search Service** (`search_service.py`)

Búsqueda híbrida inteligente:

**Algoritmo:**
1. **Búsqueda Vectorial**: Usa embeddings con `sentence-transformers`
2. **Búsqueda por Keywords**: Con diccionario de sinónimos
3. **Merge & Ranking**: Combina resultados y elimina duplicados
4. **Threshold Fallback**: Si no hay resultados, reduce umbral automáticamente

**Sinónimos integrados:**
```python
{
    'velocidad': ['rapidez', 'límite', 'máximo'],
    'multa': ['sanción', 'penalidad', 'infracción'],
    'celular': ['móvil', 'teléfono', 'dispositivo'],
    ...
}
```

### 3. **Tool Manager** (`tool_manager.py`)

Gestor de tools para function calling:

**Responsabilidades:**
- Registra tools disponibles
- Proporciona definiciones en formato Anthropic
- Ejecuta tools con parámetros del LLM
- Maneja errores de ejecución

**Tools registrados:**
- `HybridSearchTool`: Busca artículos del código
- `EmailSenderTool`: Envía emails vía ApiTool

### 4. **Tools** (`services/tools/`)

**Base Tool** (`base_tool.py`):
```python
class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del tool"""

    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción para el LLM"""

    @abstractmethod
    def get_definition(self) -> Dict[str, Any]:
        """Definición en formato Anthropic"""

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Ejecuta el tool"""
```

**Search Tool** (`search_tool.py`):
- Recibe: `consulta`, `n_resultados`, `umbral_confianza`
- Ejecuta: Búsqueda híbrida en ChromaDB
- Retorna: Lista de artículos relevantes

**Email Tool** (`email_tool.py`):
- Recibe: `to_email`, `motivo`, `mensaje`
- Ejecuta: HTTP POST a ApiTool
- Retorna: Resultado del envío

### 5. **ChromaDB Repository** (`chroma_repository.py`)

Gestión de la base de datos vectorial:

**Funciones principales:**
- `buscar_articulos()`: Búsqueda por similitud vectorial
- `obtener_estadisticas()`: Stats de la colección
- `verificar_salud()`: Health check

**Configuración:**
- Modelo de embeddings: `paraphrase-multilingual-MiniLM-L12-v2`
- Persistencia: `/app/data/chroma_db`
- Colección: `codigo_transito_colombia`

### 6. **Endpoint Principal** (`api/v1/endpoints/query.py`)

```python
POST /api/v1/query
```

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
  "answer": "Según el artículo 131 del Código Nacional de Tránsito...",
  "confidence": 0.92,
  "sources": [
    {
      "article": "Artículo 131",
      "law": "Ley 769 de 2002",
      "description": "Exceso de velocidad",
      "similarity_score": 0.95,
      "content_snippet": "..."
    }
  ],
  "processing_time": 1.25
}
```

### 7. **Dockerfile Multi-Stage**

Optimizado para producción:
- **Stage 1 (builder)**: Instala dependencias + descarga modelo de embeddings
- **Stage 2 (runtime)**: Imagen final con libgomp1 (para numpy/torch)
- Usuario no-root (`appuser`)
- Modelos pre-descargados (evita descarga en runtime)
- Puerto 8000 expuesto
- Healthcheck con start-period largo (30s)

## Requisitos Previos

- Python 3.11+
- Anthropic API Key
- Docker (para containerización)
- ~2GB espacio para ChromaDB + modelos

## Instalación Local

### 1. Instalar dependencias

```bash
cd backRag
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tu ANTHROPIC_API_KEY
```

### 3. Setup inicial de ChromaDB

```bash
python scripts/setup_database.py
```

Este script:
- Procesa documentos en `data/documents/`
- Genera embeddings con sentence-transformers
- Almacena en ChromaDB (`data/chroma_db/`)

### 4. Ejecutar servidor

```bash
python run.py
# O directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Uso con Docker

### Construcción de imagen

```bash
docker build -t backrag .
```

### Ejecutar contenedor

```bash
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e ANTHROPIC_API_KEY=your_key_here \
  backrag
```

### Con Docker Hub (Transibot)

```bash
# Pull desde Docker Hub
docker pull hugostevenpoveda692/transibot-backrag:latest

# Ejecutar
docker run -p 8000:8000 \
  -v backrag-data:/app/data \
  -e ANTHROPIC_API_KEY=your_key_here \
  -e EMAIL_SERVICE_URL=http://apistool:8076/api/v1/email/send \
  hugostevenpoveda692/transibot-backrag:latest
```

## Endpoints Disponibles

### Health Checks

- `GET /api/v1/health` - Estado del sistema y ChromaDB
- `GET /api/v1/stats` - Estadísticas de la base de datos
- `GET /api/v1/llm-status` - Estado del servicio Claude AI

### Consultas RAG

- `POST /api/v1/query` - Realizar consulta con RAG

### Documentación Automática

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Probar consulta simple

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es la multa por usar celular mientras conduzco?",
    "max_results": 3,
    "confidence_threshold": 0.4
  }'
```

### Probar function calling (búsqueda + email)

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Busca información sobre pico y placa y envíala a mi email usuario@example.com",
    "max_results": 3
  }'
```

Claude detectará automáticamente que debe:
1. Usar `buscar_articulos_transito` para encontrar info
2. Usar `enviar_email` para enviar resultados

## Integración con RouterBack

RouterBack orquesta las consultas a BackRag:

```python
# Desde RouterBack
response = await httpx.post(
    "http://backrag:8000/api/v1/query",
    json={
        "query": user_query,
        "max_results": 3,
        "confidence_threshold": 0.4
    }
)
```

**En Docker Compose:**
```yaml
environment:
  - BACKRAG_URL=http://transibot-backrag:8000
```

## Variables de Entorno Importantes

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# ChromaDB
CHROMA_DB_PATH=/app/data/chroma_db

# Embeddings
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# Claude Configuration
CLAUDE_MODEL=claude-haiku-4-5
CLAUDE_MAX_TOKENS=1024
CLAUDE_TEMPERATURE=0.7

# Search Configuration
DEFAULT_MAX_RESULTS=3
DEFAULT_CONFIDENCE_THRESHOLD=0.4

# Email Service (para EmailTool)
EMAIL_SERVICE_URL=http://apistool:8076/api/v1/email/send
```

## Troubleshooting

### Error: "ChromaDB not found"
```bash
# Ejecutar setup
python scripts/setup_database.py

# O verificar volumen
docker volume inspect transibot-backrag-data
```

### Error: "ANTHROPIC_API_KEY not configured"
```bash
# Verificar .env
echo $ANTHROPIC_API_KEY

# En Docker
docker logs transibot-backrag | grep ANTHROPIC
```

### Búsquedas lentas
- Verificar modelo de embeddings está descargado
- Revisar tamaño de ChromaDB collection
- Ajustar `max_results` y `confidence_threshold`

### Claude no usa tools
- Verificar que ToolManager está inicializado
- Revisar logs: `docker logs -f transibot-backrag`
- Confirmar que tools están en `AVAILABLE_TOOLS`

## Arquitectura RAG - Detalles Técnicos

### Pipeline de Embedding

```
Documento PDF/TXT
  │
  ▼
Chunking (fragmentos de texto)
  │
  ▼
sentence-transformers
(paraphrase-multilingual-MiniLM-L12-v2)
  │
  ▼
Vector 384-dim
  │
  ▼
ChromaDB Collection
```

### Búsqueda Híbrida

```
Query del usuario
  │
  ├──────────────┬──────────────┐
  │              │              │
  ▼              ▼              ▼
Vector       Keywords      Sinónimos
Search       Matching      Expansion
  │              │              │
  └──────────────┴──────────────┘
                 │
                 ▼
        Merge & Deduplicate
                 │
                 ▼
           Rank by Score
                 │
                 ▼
        Filter by Threshold
                 │
                 ▼
          Top N Results
```

## Seguridad

⚠️ **Buenas prácticas:**
- ✅ API key de Anthropic en variables de entorno
- ✅ Validación de inputs con Pydantic
- ✅ Rate limiting en producción (pendiente)
- ✅ Sanitización de consultas
- ✅ Usuario no-root en Docker
- ✅ CORS configurado correctamente

## Métricas y Monitoreo

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### Estadísticas ChromaDB

```bash
curl http://localhost:8000/api/v1/stats
```

### Logs

```bash
# Docker
docker logs -f transibot-backrag

# Docker Compose
docker compose logs -f backrag
```

## Mejoras Futuras

- [ ] Cache de consultas frecuentes (Redis)
- [ ] Métricas de uso (Prometheus)
- [ ] Rate limiting por usuario
- [ ] Múltiples colecciones ChromaDB
- [ ] Reranking de resultados (cross-encoder)
- [ ] Evaluación de respuestas (RAGAS)
- [ ] Soporte para imágenes en documentos
- [ ] Versionado de embeddings

## Licencia

Parte del sistema Transibot.

---

**Stack Tecnológico:**
- FastAPI 0.115+
- Anthropic SDK (Claude AI)
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- Pydantic 2.9+
- Python 3.11-slim-bookworm
- Docker multi-stage

**Puerto:** 8000
**Imagen Docker:** `hugostevenpoveda692/transibot-backrag:latest`
