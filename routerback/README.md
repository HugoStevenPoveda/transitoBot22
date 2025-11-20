# RouterBack - Orquestador de Transibot

Capa de orquestación FastAPI que actúa como **API Gateway inteligente** entre el frontend y los servicios de backend (RASA + BackRag). Implementa una estrategia de fallback automático para garantizar respuestas en todos los escenarios.

## Rol en el Sistema Transibot

RouterBack es el **orquestador central** que coordina la comunicación entre todos los servicios:

- **API Gateway**: Punto de entrada único para el frontend
- **Enrutamiento inteligente**: Decide dinámicamente si usar RASA o BackRag
- **Estrategia de fallback**: Sistema de 5 criterios para activar BackRag cuando RASA no puede responder
- **Transformación de mensajes**: Convierte formatos entre UI, RASA y BackRag
- **Gestión de sesiones**: Maneja trackers y reseteo de conversaciones

### Integración con otros servicios

```
┌──────────────┐
│   Frontend   │ ──────> Envía mensajes del usuario
│ (Port 5173)  │         POST /api/v1/chat/message
└──────────────┘
        │
        ▼
┌──────────────┐
│  RouterBack  │ ──────> 1. Recibe mensaje
│ (Port 8080)  │         2. Transforma formato
│              │         3. Decide ruta (RASA/BackRag)
└──────┬───────┘
       │
       ├──────────────────┬──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│     RASA     │  │   BackRag    │  │   ApiTool    │
│ (Port 5005)  │  │ (Port 8000)  │  │ (Port 8076)  │
│              │  │              │  │              │
│ NLU + Rules  │  │ RAG + Claude │  │ Email sender │
└──────────────┘  └──────────────┘  └──────────────┘

Flujo de decisión:
1. RASA intenta responder primero
2. RouterBack evalúa 5 criterios de fallback
3. Si cumple criterio → BackRag RAG
4. Si BackRag no responde → Mensaje genérico
```

## Arquitectura del Servicio

### Arquitectura de Decisión Inteligente

```
┌─────────────────────────────────────────────┐
│         MENSAJE DEL FRONTEND                 │
│    POST /api/v1/chat/message                 │
│    {sender_id, message, metadata}            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │  chat.py         │ ──────> Endpoint principal
         │  (FastAPI)       │         Orquestación de flujo
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ PASO 1:          │
         │ rasa_client      │ ──────> POST /webhooks/rest/webhook
         │ .send_message()  │
         └────────┬─────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │ RASA responde?              │
    │ (lista de mensajes)         │
    └────────┬────────────────────┘
             │
    ┌────────┴────────────┐
    │                     │
    SÍ                    NO
    │                     │
    ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ PASO 2:         │   │ PASO 3:         │
│ Evaluar 5       │   │ Activar BackRag │
│ criterios       │   │ (fallback)      │
│ de fallback     │   │                 │
└────┬────────────┘   └────┬────────────┘
     │                     │
     ├─ ✅ texto vacío     │
     ├─ ✅ metadata fallback│
     ├─ ✅ confianza < 60% │
     ├─ ✅ intent especial │
     └─ ✅ custom data     │
             │             │
    ┌────────┴─────────┐  │
    │                  │  │
    NO cumple    Cumple│  │
    criterio     criterio │
    │                │    │
    ▼                ▼    ▼
┌──────────┐   ┌─────────────────┐
│ Retornar │   │ backrag_client  │
│ respuesta│   │ .query()        │
│ de RASA  │   └────────┬────────┘
└──────────┘            │
                        ▼
                ┌───────────────────┐
                │ PASO 4:           │
                │ BackRag responde? │
                └────────┬──────────┘
                         │
                ┌────────┴────────┐
                │                 │
                SÍ               NO
                │                 │
                ▼                 ▼
        ┌───────────────┐  ┌───────────────┐
        │ message_      │  │ PASO 5:       │
        │ transformer   │  │ Respuesta     │
        │ .rag_to_ui()  │  │ genérica      │
        └───────┬───────┘  └───────┬───────┘
                │                  │
                └──────────┬───────┘
                           ▼
                  ┌────────────────┐
                  │ BotResponse    │
                  │ (Frontend)     │
                  └────────────────┘
```

### Arquitectura de Componentes

```
┌─────────────────────────────────────────────┐
│           FastAPI Application                │
│              (app/main.py)                   │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ Endpoints    │      │   Models     │
│ (v1/...)     │      │  (Pydantic)  │
└──────┬───────┘      └──────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│           chat.py                    │
│  ┌────────────────────────────────┐  │
│  │ POST /message                  │  │
│  │ POST /reset/{sender_id}        │  │
│  │ GET  /tracker/{sender_id}      │  │
│  └────────────────────────────────┘  │
└──────┬───────────────────────────────┘
       │
       ├───────────────┬────────────────┬──────────────┐
       │               │                │              │
       ▼               ▼                ▼              ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐
│ rasa_client │ │ backrag_     │ │ message_     │ │ Exceptions │
│             │ │ client       │ │ transformer  │ │            │
│ - send()    │ │              │ │              │ │ - HTTP     │
│ - tracker() │ │ - query()    │ │ - rasa_to_ui │ │ - Custom   │
│ - reset()   │ │ - health()   │ │ - rag_to_ui  │ │            │
│ - health()  │ │              │ │ - ui_to_rasa │ │            │
└─────────────┘ └──────────────┘ └──────────────┘ └────────────┘
       │               │
       ▼               ▼
┌─────────────┐ ┌──────────────┐
│ RASA        │ │ BackRag      │
│ (httpx)     │ │ (httpx)      │
│ Port 5005   │ │ Port 8000    │
└─────────────┘ └──────────────┘
```

## Estructura de Implementación

```
routerback/
├── app/
│   ├── __init__.py
│   ├── main.py                        # ⭐ Aplicación FastAPI principal
│   ├── config.py                      # ⭐ Configuración con pydantic-settings
│   │
│   ├── api/v1/endpoints/              # Endpoints REST
│   │   ├── __init__.py
│   │   ├── chat.py                    # ⭐ Endpoint /message (orquestación)
│   │   └── health.py                  # Health checks
│   │
│   ├── core/                          # Lógica central
│   │   ├── __init__.py
│   │   ├── rasa_client.py             # ⭐ Cliente HTTP para RASA
│   │   ├── backrag_client.py          # ⭐ Cliente HTTP para BackRag
│   │   └── message_transformer.py     # ⭐ Transformación de formatos
│   │
│   ├── models/                        # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── chat.py                    # ⭐ UserMessage, BotResponse
│   │   └── rasa.py                    # RasaRequest, RasaResponseItem
│   │
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py              # Excepciones personalizadas
│
├── tests/                             # Tests unitarios
│   └── __init__.py
│
├── Dockerfile                         # ⭐ Multi-stage build
├── requirements.txt                   # ⭐ Dependencias
├── .env.example                       # Variables de entorno ejemplo
├── .env                               # Variables de entorno (no en git)
└── README.md
```

## Elementos Importantes del Servicio

### 1. **Endpoint de Orquestación** (`chat.py`)

**POST /api/v1/chat/message** - Endpoint principal con lógica de fallback

**Características:**
- ✅ Enrutamiento dual: RASA → BackRag
- ✅ 5 criterios inteligentes de fallback
- ✅ Logging detallado de cada paso
- ✅ Manejo robusto de errores
- ✅ Respuesta genérica si todo falla

**Flujo del endpoint:**

```python
# PASO 1: Enviar a RASA primero
rasa_responses = await rasa_client.send_message(
    sender_id=user_message.sender_id,
    message=user_message.message,
    metadata=user_message.metadata
)

# PASO 2: Evaluar 5 criterios de fallback
should_use_rag = False

# Criterio 1: Texto vacío
if not first_response.text or first_response.text.strip() == "":
    should_use_rag = True
    fallback_reason = "empty_text"

# Criterio 2: Metadata custom indica fallback
elif first_response.custom and first_response.custom.get("fallback") == True:
    should_use_rag = True
    fallback_reason = first_response.custom.get("reason", "custom_fallback")

# Criterio 3: Confianza baja (<60%)
elif first_response.custom and first_response.custom.get("confidence", 1.0) < 0.6:
    should_use_rag = True
    fallback_reason = f"low_confidence_{confidence:.2f}"

# Criterio 4: Intent específico debe ir a RAG
elif intent in ["out_of_scope", "consulta_codigo_transito", "nlu_fallback"]:
    should_use_rag = True
    fallback_reason = f"intent_{intent}"

# Criterio 5: Lista de respuestas vacía
if not rasa_responses or len(rasa_responses) == 0:
    should_use_rag = True
    fallback_reason = "empty_response_list"

# PASO 3: Si cumple criterio → BackRag
if should_use_rag:
    rag_response = await backrag_client.query(message=user_message.message)
    return message_transformer.rag_to_ui(sender_id, rag_response)

# PASO 4: Si no cumple criterio → Respuesta de RASA
return message_transformer.rasa_to_ui(sender_id, rasa_responses)
```

**Request:**
```json
{
  "sender_id": "user_12345",
  "message": "Cuánto cuesta una fotomulta",
  "metadata": {
    "channel": "web",
    "session_id": "abc123"
  }
}
```

**Response:**
```json
{
  "sender_id": "user_12345",
  "messages": [
    {
      "text": "Las fotomultas varían según el tipo de infracción...",
      "image": null,
      "buttons": null,
      "custom": {
        "source": "rasa",
        "intent": "costos_fotomulta",
        "confidence": 0.92
      }
    }
  ],
  "timestamp": "2025-11-20T10:30:00Z"
}
```

**Otros endpoints:**

```python
# GET /api/v1/chat/tracker/{sender_id}
# Obtiene el estado de conversación de RASA

# POST /api/v1/chat/reset/{sender_id}
# Reinicia la conversación de un usuario
```

### 2. **Cliente RASA** (`rasa_client.py`)

**Características:**
- ✅ Cliente HTTP asíncrono con httpx
- ✅ Métodos para envío, tracker, reset
- ✅ Health check de RASA
- ✅ Timeout configurable (30s default)

**Métodos principales:**

```python
class RasaClient:
    async def send_message(
        self,
        sender_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[RasaResponseItem]:
        """
        Envía mensaje a RASA webhook
        POST http://rasa:5005/webhooks/rest/webhook
        """

    async def get_tracker(self, sender_id: str) -> Optional[RasaTrackerResponse]:
        """
        Obtiene el tracker de conversación
        GET http://rasa:5005/conversations/{sender_id}/tracker
        """

    async def reset_tracker(self, sender_id: str) -> bool:
        """
        Reinicia la conversación
        POST http://rasa:5005/conversations/{sender_id}/tracker/events
        Envía: {"event": "restart"}
        """

    async def health_check(self) -> bool:
        """
        Verifica salud del servicio
        GET http://rasa:5005/status
        """
```

**Formato de request a RASA:**
```python
RasaRequest(
    sender="user_12345",
    message="Hola",
    metadata={"channel": "web"}
)
```

**Formato de response de RASA:**
```python
[
    RasaResponseItem(
        text="Hola! ¿En qué puedo ayudarte?",
        image=None,
        buttons=None,
        custom={"intent": "saludo", "confidence": 0.98}
    )
]
```

### 3. **Cliente BackRag** (`backrag_client.py`)

**Características:**
- ✅ Cliente HTTP asíncrono para RAG
- ✅ Query con parámetros configurables
- ✅ Health check de BackRag
- ✅ Timeout configurable (30s default)
- ✅ Manejo robusto de errores (TimeoutException, HTTPError)

**Método principal:**

```python
class BackRagClient:
    async def query(
        self,
        message: str,
        max_results: int = 3,
        confidence_threshold: float = 0.4
    ) -> Optional[Dict[str, Any]]:
        """
        Consulta BackRag RAG service
        POST http://backrag:8000/api/v1/query
        """

    async def health_check(self) -> bool:
        """
        Verifica salud del servicio
        GET http://backrag:8000/api/v1/health
        """
```

**Formato de request a BackRag:**
```json
{
  "query": "Qué pasa si mi carro está mal parqueado",
  "max_results": 3,
  "confidence_threshold": 0.4
}
```

**Formato de response de BackRag:**
```json
{
  "answer": "Según el Artículo 131 del Código Nacional de Tránsito...",
  "confidence": 0.87,
  "sources": [
    {
      "article": "Artículo 131",
      "law": "Código Nacional de Tránsito",
      "score": 0.92
    }
  ],
  "processing_time": 1.234
}
```

### 4. **Transformador de Mensajes** (`message_transformer.py`)

**Características:**
- ✅ Transforma entre 3 formatos: UI ↔ RASA ↔ BackRag
- ✅ Preserva metadata custom
- ✅ Agrega timestamps
- ✅ Formatea fuentes de BackRag

**Métodos:**

```python
class MessageTransformer:
    @staticmethod
    def ui_to_rasa(user_message: UserMessage) -> RasaRequest:
        """UI → RASA"""

    @staticmethod
    def rasa_to_ui(
        sender_id: str,
        rasa_responses: List[RasaResponseItem]
    ) -> BotResponse:
        """RASA → UI"""

    @staticmethod
    def rag_to_ui(
        sender_id: str,
        rag_response: Dict[str, Any]
    ) -> BotResponse:
        """BackRag → UI (incluye fuentes)"""
```

**Transformación RAG → UI:**

```python
# Input: Respuesta de BackRag
{
  "answer": "Artículo 131...",
  "confidence": 0.87,
  "sources": [...]
}

# Output: BotResponse para UI
BotResponse(
    sender_id="user_12345",
    messages=[
        BotMessageItem(
            text="Artículo 131...",
            custom={
                "source": "backrag",
                "confidence": 0.87,
                "sources_count": 3
            }
        ),
        BotMessageItem(
            text="📚 Fuentes consultadas:\n1. Artículo 131...",
            custom={"type": "sources"}
        )
    ],
    timestamp="2025-11-20T10:30:00Z"
)
```

### 5. **Modelos Pydantic** (`models/chat.py`)

**UserMessage** - Request del frontend:
```python
class UserMessage(BaseModel):
    sender_id: str          # ID único del usuario
    message: str            # Mensaje del usuario
    metadata: Optional[Dict[str, Any]]  # Metadata adicional
```

**BotMessageItem** - Mensaje individual del bot:
```python
class BotMessageItem(BaseModel):
    text: Optional[str]     # Texto del mensaje
    image: Optional[str]    # URL de imagen
    buttons: Optional[List[Dict[str, str]]]  # Botones de acción
    custom: Optional[Dict[str, Any]]  # Datos personalizados
```

**BotResponse** - Response al frontend:
```python
class BotResponse(BaseModel):
    sender_id: str          # ID del usuario
    messages: List[BotMessageItem]  # Lista de mensajes
    timestamp: datetime     # Timestamp UTC
```

### 6. **Configuración** (`config.py`)

**Características:**
- ✅ Gestión con pydantic-settings
- ✅ Carga desde .env
- ✅ Validación automática de tipos
- ✅ Valores por defecto

```python
class Settings(BaseSettings):
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

    # BackRag
    backrag_url: str = "http://localhost:8001"
    backrag_query_path: str = "/api/v1/query"
    backrag_timeout: int = 30

    # CORS
    cors_origins: list = ["*"]
```

**Configuración en Docker:**
```yaml
environment:
  - RASA_URL=http://transibot-rasa:5005
  - BACKRAG_URL=http://transibot-backrag:8000
  - PORT=8080
  - CORS_ORIGINS=["*"]
```

### 7. **Aplicación FastAPI** (`main.py`)

**Características:**
- ✅ CORS habilitado para frontend
- ✅ Documentación automática (Swagger + ReDoc)
- ✅ Eventos de startup/shutdown
- ✅ Logging configurado
- ✅ Versionado de API (v1)

```python
app = FastAPI(
    title=settings.app_name,
    description="Capa de orquestación para comunicación con RASA",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
```

### 8. **Dockerfile Multi-Stage**

Optimizado para producción:
- **Stage 1 (builder)**: Instala dependencias con uv
- **Stage 2 (runtime)**: Imagen final ligera
- Usuario no-root (`appuser`)
- Puerto 8080 expuesto
- Healthcheck integrado

## Estrategia de Fallback Inteligente

RouterBack implementa 5 criterios para decidir cuándo activar BackRag:

```
┌────────────────────────────────────────────────┐
│     CRITERIOS DE FALLBACK A BACKRAG            │
├────────────────────────────────────────────────┤
│ 1. Texto vacío                                 │
│    → first_response.text == ""                 │
│                                                │
│ 2. Metadata indica fallback                    │
│    → custom.get("fallback") == True            │
│                                                │
│ 3. Confianza baja                              │
│    → custom.get("confidence") < 0.6            │
│                                                │
│ 4. Intent específico para RAG                  │
│    → intent in ["out_of_scope",                │
│                 "consulta_codigo_transito",    │
│                 "nlu_fallback"]                │
│                                                │
│ 5. Lista de respuestas vacía                   │
│    → len(rasa_responses) == 0                  │
└────────────────────────────────────────────────┘
```

**Ejemplo de evaluación:**

```python
# Escenario 1: Intent con baja confianza (45%)
rasa_response = {
    "text": "No estoy seguro de lo que preguntas",
    "custom": {
        "intent": "nlu_fallback",
        "confidence": 0.45
    }
}
# Resultado: ✅ Activa BackRag (criterio 3 + 4)

# Escenario 2: Respuesta clara con alta confianza (92%)
rasa_response = {
    "text": "Las fotomultas varían según el tipo...",
    "custom": {
        "intent": "costos_fotomulta",
        "confidence": 0.92
    }
}
# Resultado: ❌ NO activa BackRag, usa respuesta de RASA

# Escenario 3: RASA envía fallback explícito
rasa_response = {
    "text": "",
    "custom": {
        "fallback": True,
        "reason": "openrouter_failed_then_backrag"
    }
}
# Resultado: ✅ Activa BackRag (criterio 1 + 2)
```

## Flujo de Conversación Completo

### Escenario 1: Consulta manejada por RASA

```
Usuario: "Hola"
   ↓
Frontend → RouterBack
   POST /api/v1/chat/message
   {sender_id: "user_123", message: "Hola"}
   ↓
RouterBack → RASA
   POST http://rasa:5005/webhooks/rest/webhook
   {sender: "user_123", message: "Hola"}
   ↓
RASA responde:
   [{
     "text": "Hola! ¿En qué puedo ayudarte?",
     "custom": {"intent": "saludo", "confidence": 0.98}
   }]
   ↓
RouterBack evalúa criterios:
   ❌ Texto NO vacío
   ❌ NO tiene metadata fallback
   ❌ Confianza alta (0.98)
   ❌ Intent NO es out_of_scope
   ❌ Lista NO vacía
   → NO activa BackRag
   ↓
message_transformer.rasa_to_ui()
   ↓
Frontend recibe:
   {
     "sender_id": "user_123",
     "messages": [{
       "text": "Hola! ¿En qué puedo ayudarte?",
       "custom": {"source": "rasa", "intent": "saludo"}
     }],
     "timestamp": "2025-11-20T10:30:00Z"
   }
```

### Escenario 2: Fallback a BackRag (baja confianza)

```
Usuario: "Qué pasa si mi carro está mal parqueado"
   ↓
Frontend → RouterBack
   POST /api/v1/chat/message
   ↓
RouterBack → RASA
   POST http://rasa:5005/webhooks/rest/webhook
   ↓
RASA responde:
   [{
     "text": "No estoy seguro",
     "custom": {"intent": "nlu_fallback", "confidence": 0.45}
   }]
   ↓
RouterBack evalúa criterios:
   ❌ Texto NO vacío
   ❌ NO tiene metadata fallback
   ✅ Confianza baja (0.45 < 0.6)  ← CRITERIO CUMPLIDO
   ✅ Intent "nlu_fallback"         ← CRITERIO CUMPLIDO
   → SÍ activa BackRag
   ↓
RouterBack → BackRag
   POST http://backrag:8000/api/v1/query
   {
     "query": "Qué pasa si mi carro está mal parqueado",
     "max_results": 3,
     "confidence_threshold": 0.4
   }
   ↓
BackRag responde:
   {
     "answer": "Según el Artículo 131 del CNT, el parqueo...",
     "confidence": 0.87,
     "sources": [{...}],
     "processing_time": 1.234
   }
   ↓
message_transformer.rag_to_ui()
   ↓
Frontend recibe:
   {
     "sender_id": "user_123",
     "messages": [
       {
         "text": "Según el Artículo 131 del CNT...",
         "custom": {"source": "backrag", "confidence": 0.87}
       },
       {
         "text": "📚 Fuentes consultadas:\n1. Artículo 131...",
         "custom": {"type": "sources"}
       }
     ],
     "timestamp": "2025-11-20T10:30:00Z"
   }
```

### Escenario 3: Fallback total (ambos servicios fallan)

```
Usuario: "¿Qué es XYZ?"
   ↓
RouterBack → RASA
   ↓
RASA responde: []  (lista vacía)
   ↓
RouterBack evalúa:
   ✅ Lista vacía → Activa BackRag
   ↓
RouterBack → BackRag
   ↓
BackRag responde: None  (error de timeout o conexión)
   ↓
RouterBack activa respuesta genérica:
   {
     "messages": [{
       "text": "Lo siento, en este momento no puedo procesar tu consulta...",
       "custom": {"source": "fallback_error"}
     }]
   }
```

## Instalación Local

### Requisitos previos

- Python 3.11+
- RASA corriendo en puerto 5005
- BackRag corriendo en puerto 8000

### Instalación

```bash
cd routerback

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o .venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
```

### Ejecutar

```bash
# Opción 1: uvicorn directamente
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# Opción 2: Python script
python -m app.main
```

La aplicación estará disponible en:
- API: http://localhost:8080
- Swagger: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Uso con Docker

### Construcción de imagen

```bash
docker build -t transibot-routerback .
```

### Con Docker Hub (Transibot)

```bash
# Pull desde Docker Hub
docker pull hugostevenpoveda692/transibot-routerback:latest

# Ejecutar
docker run -p 8080:8080 \
  -e RASA_URL=http://transibot-rasa:5005 \
  -e BACKRAG_URL=http://transibot-backrag:8000 \
  hugostevenpoveda692/transibot-routerback:latest
```

### Healthcheck

```bash
# Root endpoint
curl http://localhost:8080/

# Health check
curl http://localhost:8080/api/v1/health

# Response:
# {
#   "status": "healthy",
#   "rasa_connected": true,
#   "backrag_connected": true,
#   "timestamp": "2025-11-20T10:30:00Z"
# }
```

## Endpoints Disponibles

### Health Checks

- `GET /` - Información de la API
- `GET /api/v1/health` - Health check completo

### Chat

- `POST /api/v1/chat/message` - Enviar mensaje al bot
- `GET /api/v1/chat/tracker/{sender_id}` - Obtener estado de conversación
- `POST /api/v1/chat/reset/{sender_id}` - Reiniciar conversación

### Documentación

- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc
- `GET /openapi.json` - OpenAPI JSON

## Testing

### Usando curl

```bash
# Health check
curl http://localhost:8080/api/v1/health

# Enviar mensaje
curl -X POST http://localhost:8080/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "user_123",
    "message": "Hola"
  }'

# Obtener tracker
curl http://localhost:8080/api/v1/chat/tracker/user_123

# Reiniciar conversación
curl -X POST http://localhost:8080/api/v1/chat/reset/user_123
```

### Usando HTTPie

```bash
# Health check
http GET http://localhost:8080/api/v1/health

# Enviar mensaje
http POST http://localhost:8080/api/v1/chat/message \
  sender_id=user_123 \
  message="Hola"
```

## Integración con Frontend

El frontend consume RouterBack como API única:

**Desde Frontend (React):**
```typescript
// src/services/api.ts
const API_BASE_URL = "http://localhost:8080";

export const sendMessage = async (
  message: string,
  senderId: string
): Promise<BotResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sender_id: senderId,
      message: message,
      metadata: { channel: "web" }
    })
  });
  return response.json();
};
```

**En Docker Compose:**
```yaml
services:
  frontend:
    environment:
      - VITE_API_URL=http://transibot-routerback:8080
```

## Troubleshooting

### Error: "RASA not connected" en /health

```bash
# Verificar que RASA está corriendo
curl http://localhost:5005/status

# En Docker, verificar network
docker compose exec routerback ping transibot-rasa

# Revisar logs
docker compose logs -f routerback
docker compose logs -f rasa
```

### Error: "BackRag not connected" en /health

```bash
# Verificar que BackRag está corriendo
curl http://localhost:8000/api/v1/health

# En Docker, verificar network
docker compose exec routerback ping transibot-backrag

# Revisar logs
docker compose logs -f backrag
```

### Timeout al consultar servicios

```bash
# Incrementar timeouts en .env
RASA_TIMEOUT=60
BACKRAG_TIMEOUT=60

# Reiniciar contenedor
docker compose restart routerback
```

### Error de CORS

```bash
# Verificar CORS_ORIGINS en .env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# En producción, especificar dominios permitidos
CORS_ORIGINS=["https://transibot.example.com"]
```

### Logs no aparecen

```bash
# Ver logs en tiempo real
docker compose logs -f routerback

# Ver últimos 100 logs
docker compose logs --tail=100 routerback

# Logs incluyen:
# [Chat] Recibido de sender_id=...
# [Chat] PASO 1: Enviando mensaje a RASA...
# [Chat] Criterio 3: Baja confianza detectada
# [Chat] PASO 3: Activando fallback a BackRag
```

## Logs y Debugging

El servicio genera logs detallados de cada paso:

```
2025-11-20 10:30:00 - app.api.v1.endpoints.chat - INFO - ========== NUEVO MENSAJE ==========
2025-11-20 10:30:00 - app.api.v1.endpoints.chat - INFO - [Chat] Recibido de sender_id=user_123: 'Hola'
2025-11-20 10:30:00 - app.api.v1.endpoints.chat - INFO - [Chat] PASO 1: Enviando mensaje a RASA...
2025-11-20 10:30:01 - app.core.rasa_client - INFO - Enviando mensaje a RASA: sender=user_123, message=Hola
2025-11-20 10:30:02 - app.core.rasa_client - INFO - Respuesta de RASA: 1 mensajes
2025-11-20 10:30:02 - app.api.v1.endpoints.chat - INFO - ========== RASA RESPONDE ==========
2025-11-20 10:30:02 - app.api.v1.endpoints.chat - INFO - [Chat] Respuestas recibidas de RASA: 1
2025-11-20 10:30:02 - app.api.v1.endpoints.chat - INFO - [Chat] ✓ RASA respondió con 1 mensaje(s)
2025-11-20 10:30:02 - app.api.v1.endpoints.chat - INFO - [Chat] ✓ RASA manejó la consulta exitosamente
2025-11-20 10:30:02 - app.api.v1.endpoints.chat - INFO - [Chat] Respuesta final enviada (origen: RASA) - 1 mensaje(s)
2025-11-20 10:30:02 - app.api.v1.endpoints.chat - INFO - ========== FIN PROCESAMIENTO ==========
```

## Mejoras Futuras

- [ ] Rate limiting por usuario
- [ ] Cache de respuestas frecuentes
- [ ] Métricas con Prometheus
- [ ] Circuit breaker para servicios caídos
- [ ] Retry automático con backoff exponencial
- [ ] A/B testing de estrategias de fallback
- [ ] WebSocket para chat en tiempo real
- [ ] Queue de mensajes con RabbitMQ/Redis

## Licencia

Parte del sistema Transibot.

---

**Stack Tecnológico:**
- FastAPI 0.115+
- Pydantic 2.9+
- httpx (async HTTP client)
- uvicorn (ASGI server)
- Python 3.11-slim-bookworm
- Docker multi-stage

**Puerto:** 8080

**Imagen Docker:** `hugostevenpoveda692/transibot-routerback:latest`

**Rol:** API Gateway con estrategia de fallback inteligente (RASA → BackRag → Genérico)
