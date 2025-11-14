# Arquitectura Propuesta con Redis - TránsitoBot Soacha

## 📋 Información General

**Versión:** 2.0 (Propuesta con Redis)
**Fecha:** 2025-10-30
**Cambio Principal:** Integración de Redis para gestión de memoria conversacional y contexto

---

## 🎯 Objetivos de la Integración de Redis

### Problemas Actuales
- ❌ No hay persistencia de historial conversacional entre componentes
- ❌ RASA y BackRag no comparten contexto del usuario
- ❌ Sin caché de respuestas frecuentes
- ❌ Cada consulta a BackRag es independiente (sin memoria)
- ❌ No hay seguimiento de sesiones de usuario

### Soluciones con Redis
- ✅ **Memoria conversacional persistente** - Historial completo de cada usuario
- ✅ **Contexto compartido** - RASA y BackRag acceden al mismo contexto
- ✅ **Caché inteligente** - Respuestas frecuentes en cache
- ✅ **Sesiones de usuario** - Tracking de estado y metadata
- ✅ **Contexto para LLM** - Claude AI recibe historial relevante
- ✅ **Performance mejorado** - Reducción de latencia

---

## 🏗️ Arquitectura Propuesta con Redis

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                   │
│                   http://localhost:5173                      │
│                                                               │
│  - Interfaz conversacional                                   │
│  - Mantiene conversación completa en UI                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST + session_id
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              ROUTERBACK (FastAPI - Orquestador)              │
│                   http://localhost:8080                      │
│                                                               │
│  NUEVA LÓGICA CON REDIS:                                     │
│  1. Recibe mensaje + session_id                              │
│  2. Consulta Redis: obtiene historial conversacional         │
│  3. Enriquece mensaje con contexto                           │
│  4. Envía a RASA con contexto                                │
│  5. Si RASA falla → BackRag con contexto completo            │
│  6. Guarda respuesta en Redis                                │
│  7. Actualiza historial conversacional                       │
└──────────┬─────────────────────────┬────────┬───────────────┘
           │                         │        │
           ↓                         ↓        ↓
    ┌──────────┐            ┌────────────┐   │
    │   RASA   │            │  BACKRAG   │   │
    │  :5005   │            │   :8000    │   │
    │  :5055   │            └────────────┘   │
    └──────────┘                 │            │
           │                     │            │
           │                     ↓            │
           │            ┌─────────────────┐   │
           │            │   ChromaDB      │   │
           │            │  (192 arts.)    │   │
           │            └─────────────────┘   │
           │                     │            │
           │                     ↓            │
           │            ┌─────────────────┐   │
           │            │   Claude AI     │   │
           │            │  (Anthropic)    │   │
           │            └─────────────────┘   │
           │                                  │
           └──────────────┬───────────────────┘
                          ↓
            ┌──────────────────────────────────┐
            │         REDIS (Cache Layer)       │
            │        http://localhost:6379      │
            │                                   │
            │  ALMACENA:                        │
            │  ├─ Historial conversacional      │
            │  │  Key: chat:history:{session}   │
            │  │  Value: [mensaje1, msg2, ...]  │
            │  │                                │
            │  ├─ Contexto de usuario           │
            │  │  Key: user:context:{session}   │
            │  │  Value: {metadata, state}      │
            │  │                                │
            │  ├─ Cache de respuestas           │
            │  │  Key: cache:query:{hash}       │
            │  │  Value: {answer, sources}      │
            │  │  TTL: 1 hora                   │
            │  │                                │
            │  ├─ Sesiones activas              │
            │  │  Key: session:{id}             │
            │  │  Value: {user, created_at}     │
            │  │  TTL: 24 horas                 │
            │  │                                │
            │  └─ Estado de conversación RASA   │
            │     Key: rasa:tracker:{sender}    │
            │     Value: {slots, intent}        │
            └──────────────────────────────────┘
```

---

## 🔄 Flujos de Datos Actualizados

### Flujo 1: Usuario Envía Mensaje (Con Redis)

```
┌────────┐
│ Usuario│
└───┬────┘
    │
    │ 1. "¿Cuál es la multa por exceso de velocidad?"
    │    + session_id: "abc123"
    ↓
┌──────────────┐
│  Frontend    │
└──────┬───────┘
       │
       │ 2. POST /api/v1/chat/message
       │    {session_id, message, metadata}
       ↓
┌──────────────────────────────────────────────────┐
│              RouterBack                          │
│                                                  │
│  3. Consulta Redis: Historial conversacional    │
│     GET chat:history:abc123                      │
│     → [msg1, msg2, msg3, ...]                    │
│                                                  │
│  4. Enriquece mensaje con contexto:              │
│     - Últimos 5 mensajes                         │
│     - Metadata de usuario                        │
│     - Estado de conversación                     │
│                                                  │
│  5. Decisión de routing...                       │
└──────────┬───────────────────────────────────────┘
           │
           ↓
    ┌─────────────┐
    │  ¿RASA?     │
    └─────┬───┬───┘
          │   │
    SÍ    │   │  NO (vacío/error)
          ↓   ↓
       [RASA] [BackRag + Redis]
```

---

### Flujo 2: RASA con Contexto desde Redis

```
RouterBack → Redis: GET user:context:abc123
                   → {name: "Juan", last_intent: "consultar_multas"}

RouterBack → RASA: POST /webhooks/rest/webhook
                   {
                     "sender": "abc123",
                     "message": "¿Y cuánto cuesta?",
                     "metadata": {
                       "context": {
                         "last_intent": "consultar_multas",
                         "last_entity": "exceso_velocidad"
                       }
                     }
                   }

RASA → RouterBack: [{"text": "La multa tipo C cuesta..."}]

RouterBack → Redis:
  - ZADD chat:history:abc123 timestamp "{role: 'user', msg: '¿Y cuánto cuesta?'}"
  - ZADD chat:history:abc123 timestamp "{role: 'bot', msg: 'La multa tipo C...'}"
  - SET user:context:abc123 "{last_intent: 'consultar_multas', ...}" EX 86400

RouterBack → Frontend: Respuesta
```

---

### Flujo 3: BackRag con Memoria Conversacional (LLM Context)

```
RouterBack → Redis: ZRANGE chat:history:abc123 -10 -1
                   → Últimos 10 mensajes de la conversación

RouterBack → BackRag: POST /api/v1/query
                      {
                        "query": "¿Y si es en zona escolar?",
                        "conversation_history": [
                          {role: "user", content: "¿Multa por exceso?"},
                          {role: "assistant", content: "La multa es..."},
                          {role: "user", content: "¿Y si es en zona escolar?"}
                        ],
                        "session_id": "abc123"
                      }

BackRag → Redis: GET cache:query:hash("multa_zona_escolar")
                → MISS (no está en cache)

BackRag → ChromaDB: Vector search con contexto mejorado

BackRag → Claude AI:
  POST /v1/messages
  {
    "system": "Eres un asistente legal...",
    "messages": [
      {"role": "user", "content": "¿Multa por exceso?"},
      {"role": "assistant", "content": "La multa es..."},
      {"role": "user", "content": "¿Y si es en zona escolar?"}
    ],
    "context": [
      {article: "Art. 131", content: "..."},
      {article: "Art. 132", content: "..."}
    ]
  }

Claude AI → BackRag: Respuesta contextualizada

BackRag → Redis:
  - SET cache:query:hash("multa_zona_escolar") "{answer, sources}" EX 3600
  - Actualizar historial

BackRag → RouterBack → Frontend: Respuesta con contexto
```

---

### Flujo 4: Cache de Respuestas Frecuentes

```
Usuario: "¿Cuál es el número de emergencias de tránsito?"

RouterBack → Redis: GET cache:query:hash("numero_emergencias_transito")
                   → HIT! {
                       "answer": "El número de emergencias es...",
                       "cached_at": "2025-10-30 10:00:00",
                       "ttl": 3500
                     }

RouterBack → Frontend: Respuesta desde cache (< 5ms)
                      + metadata: {from_cache: true}

// No consulta ni RASA ni BackRag - respuesta instantánea
```

---

## 🗄️ Estructura de Datos en Redis

### 1. Historial Conversacional (Sorted Set)

**Key:** `chat:history:{session_id}`
**Tipo:** Sorted Set (ordenado por timestamp)
**TTL:** 7 días

```redis
ZADD chat:history:abc123 1730300000 '{"role":"user","content":"Hola","timestamp":"2025-10-30T10:00:00Z"}'
ZADD chat:history:abc123 1730300001 '{"role":"assistant","content":"¡Hola! ¿En qué puedo ayudarte?","timestamp":"2025-10-30T10:00:01Z","source":"RASA"}'
ZADD chat:history:abc123 1730300030 '{"role":"user","content":"¿Multa por pico y placa?","timestamp":"2025-10-30T10:00:30Z"}'
ZADD chat:history:abc123 1730300032 '{"role":"assistant","content":"Según el Art. 131...","timestamp":"2025-10-30T10:00:32Z","source":"BackRag"}'

// Obtener últimos 10 mensajes
ZRANGE chat:history:abc123 -10 -1
```

**Estructura de cada mensaje:**
```json
{
  "role": "user | assistant",
  "content": "texto del mensaje",
  "timestamp": "ISO 8601",
  "source": "RASA | BackRag | cache",
  "metadata": {
    "intent": "consultar_multas",
    "confidence": 0.85,
    "articles_used": ["Art. 131"]
  }
}
```

---

### 2. Contexto de Usuario (Hash)

**Key:** `user:context:{session_id}`
**Tipo:** Hash
**TTL:** 24 horas

```redis
HSET user:context:abc123 last_intent "consultar_multas"
HSET user:context:abc123 last_entity "pico_y_placa"
HSET user:context:abc123 user_location "Soacha"
HSET user:context:abc123 conversation_stage "gathering_info"
HSET user:context:abc123 created_at "2025-10-30T10:00:00Z"
HSET user:context:abc123 last_activity "2025-10-30T10:05:00Z"

// Obtener todo el contexto
HGETALL user:context:abc123
```

**Campos:**
- `last_intent`: Último intent detectado por RASA
- `last_entity`: Última entidad extraída
- `user_location`: Ubicación del usuario (si aplica)
- `conversation_stage`: Etapa de la conversación
- `created_at`: Inicio de sesión
- `last_activity`: Última actividad
- `custom_data`: Metadata adicional (JSON string)

---

### 3. Cache de Respuestas (String con JSON)

**Key:** `cache:query:{query_hash}`
**Tipo:** String (JSON serializado)
**TTL:** 1 hora (ajustable según frecuencia)

```redis
SET cache:query:5f3a8b2c '{
  "query": "¿Cuál es la multa por exceso de velocidad?",
  "answer": "Según el Artículo 131...",
  "confidence": 0.92,
  "sources": [...],
  "cached_at": "2025-10-30T10:00:00Z",
  "hit_count": 15
}' EX 3600

// Incrementar contador de hits
INCR cache:query:5f3a8b2c:hits
```

**Estrategia de cache:**
- Queries exactas → hash MD5 de la consulta normalizada
- TTL dinámico: preguntas frecuentes (24h), otras (1h)
- Invalidación manual si datos cambian

---

### 4. Sesiones Activas (Hash)

**Key:** `session:{session_id}`
**Tipo:** Hash
**TTL:** 24 horas (renovable con actividad)

```redis
HSET session:abc123 user_id "user_123"
HSET session:abc123 channel "web"
HSET session:abc123 created_at "2025-10-30T10:00:00Z"
HSET session:abc123 last_seen "2025-10-30T10:05:00Z"
HSET session:abc123 message_count "12"
HSET session:abc123 device "desktop"

// Renovar TTL con actividad
EXPIRE session:abc123 86400
```

---

### 5. Estado de Tracker RASA (String con JSON)

**Key:** `rasa:tracker:{sender_id}`
**Tipo:** String (JSON)
**TTL:** 24 horas

```redis
SET rasa:tracker:abc123 '{
  "sender_id": "abc123",
  "slots": {
    "tipo_consulta": "multas",
    "tipo_infraccion": "exceso_velocidad"
  },
  "latest_intent": {
    "name": "consultar_multas",
    "confidence": 0.95
  },
  "latest_message": {
    "text": "¿Cuánto cuesta?",
    "intent_ranking": [...]
  },
  "active_loop": null,
  "latest_action_name": "action_consultar_multa"
}' EX 86400
```

---

### 6. Analytics y Métricas (Counters y Sorted Sets)

```redis
// Contador de consultas por día
INCR analytics:queries:2025-10-30

// Queries más frecuentes (por popularidad)
ZINCRBY analytics:popular_queries 1 "multa_exceso_velocidad"

// Latencia promedio
LPUSH analytics:latency:backrag 245
LTRIM analytics:latency:backrag 0 999  // Mantener últimos 1000

// Rate limiting por usuario
INCR rate_limit:user_123:2025-10-30:10
EXPIRE rate_limit:user_123:2025-10-30:10 3600
```

---

## 🔧 Implementación Técnica

### Cambios en RouterBack

**Nuevo archivo:** `routerback/app/core/redis_client.py`

```python
from redis import Redis
from typing import List, Dict, Optional
import json
import hashlib
from datetime import datetime

class RedisManager:
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis = Redis(host=host, port=port, decode_responses=True)

    # ===== HISTORIAL CONVERSACIONAL =====

    def add_message_to_history(
        self,
        session_id: str,
        role: str,
        content: str,
        source: str = None,
        metadata: dict = None
    ):
        """Agrega un mensaje al historial conversacional"""
        timestamp = datetime.utcnow().timestamp()
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "metadata": metadata or {}
        }

        key = f"chat:history:{session_id}"
        self.redis.zadd(key, {json.dumps(message): timestamp})
        self.redis.expire(key, 7 * 24 * 3600)  # 7 días

    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Obtiene los últimos N mensajes de la conversación"""
        key = f"chat:history:{session_id}"
        messages = self.redis.zrange(key, -limit, -1)
        return [json.loads(msg) for msg in messages]

    # ===== CONTEXTO DE USUARIO =====

    def update_user_context(
        self,
        session_id: str,
        context_data: dict
    ):
        """Actualiza el contexto del usuario"""
        key = f"user:context:{session_id}"
        for field, value in context_data.items():
            self.redis.hset(key, field, value)
        self.redis.expire(key, 24 * 3600)  # 24 horas

    def get_user_context(self, session_id: str) -> Dict:
        """Obtiene el contexto completo del usuario"""
        key = f"user:context:{session_id}"
        return self.redis.hgetall(key) or {}

    # ===== CACHE DE RESPUESTAS =====

    def get_cached_response(self, query: str) -> Optional[Dict]:
        """Busca respuesta en cache"""
        query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
        key = f"cache:query:{query_hash}"
        cached = self.redis.get(key)

        if cached:
            # Incrementar hit count
            self.redis.incr(f"{key}:hits")
            return json.loads(cached)
        return None

    def cache_response(
        self,
        query: str,
        response: dict,
        ttl: int = 3600
    ):
        """Guarda respuesta en cache"""
        query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
        key = f"cache:query:{query_hash}"

        cache_data = {
            **response,
            "cached_at": datetime.utcnow().isoformat(),
            "query": query
        }

        self.redis.setex(key, ttl, json.dumps(cache_data))

    # ===== SESIONES =====

    def create_session(
        self,
        session_id: str,
        user_data: dict
    ):
        """Crea o actualiza una sesión"""
        key = f"session:{session_id}"
        session_data = {
            **user_data,
            "created_at": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            "message_count": "0"
        }

        for field, value in session_data.items():
            self.redis.hset(key, field, value)
        self.redis.expire(key, 24 * 3600)

    def update_session_activity(self, session_id: str):
        """Actualiza última actividad de sesión"""
        key = f"session:{session_id}"
        self.redis.hset(key, "last_seen", datetime.utcnow().isoformat())
        self.redis.hincrby(key, "message_count", 1)
        self.redis.expire(key, 24 * 3600)  # Renovar TTL
```

---

**Actualización:** `routerback/app/api/v1/endpoints/chat.py`

```python
from app.core.redis_client import RedisManager

redis_manager = RedisManager()

@router.post("/message")
async def send_message(user_message: UserMessage):
    session_id = user_message.sender_id

    # 1. Verificar cache primero
    cached_response = redis_manager.get_cached_response(user_message.message)
    if cached_response:
        logger.info(f"[Cache] Respuesta encontrada en cache para: {user_message.message[:50]}")
        return cached_response

    # 2. Obtener historial conversacional
    conversation_history = redis_manager.get_conversation_history(session_id, limit=10)
    user_context = redis_manager.get_user_context(session_id)

    # 3. Guardar mensaje del usuario en historial
    redis_manager.add_message_to_history(
        session_id=session_id,
        role="user",
        content=user_message.message
    )

    # 4. Actualizar actividad de sesión
    redis_manager.update_session_activity(session_id)

    # 5. Enviar a RASA con contexto
    rasa_response = await send_to_rasa(
        sender_id=session_id,
        message=user_message.message,
        context=user_context
    )

    if rasa_response:
        # 6a. RASA respondió
        redis_manager.add_message_to_history(
            session_id=session_id,
            role="assistant",
            content=rasa_response["text"],
            source="RASA"
        )

        # Actualizar contexto con intent detectado
        if "intent" in rasa_response.get("metadata", {}):
            redis_manager.update_user_context(session_id, {
                "last_intent": rasa_response["metadata"]["intent"]
            })

        return rasa_response

    else:
        # 6b. Fallback a BackRag con historial
        backrag_response = await send_to_backrag(
            query=user_message.message,
            conversation_history=conversation_history,
            session_id=session_id
        )

        # Guardar respuesta en historial
        redis_manager.add_message_to_history(
            session_id=session_id,
            role="assistant",
            content=backrag_response["answer"],
            source="BackRag",
            metadata={
                "confidence": backrag_response["confidence"],
                "articles": [s["article"] for s in backrag_response["sources"]]
            }
        )

        # Cache respuestas de alta confianza
        if backrag_response["confidence"] > 0.75:
            redis_manager.cache_response(
                query=user_message.message,
                response=backrag_response,
                ttl=3600  # 1 hora
            )

        return backrag_response
```

---

### Cambios en BackRag

**Actualización:** `backRag/app/services/llm_service.py`

```python
class LLMService:
    def generate_response(
        self,
        query: str,
        context: List[Dict],
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Genera respuesta usando Claude AI con historial conversacional
        """
        # Construir mensajes con historial
        messages = []

        # Agregar historial si existe
        if conversation_history:
            for msg in conversation_history[-5:]:  # Últimos 5 mensajes
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Agregar consulta actual con contexto de artículos
        context_text = self._format_context(context)
        current_message = f"""
Consulta: {query}

Contexto legal relevante:
{context_text}

Por favor responde basándote en el contexto legal proporcionado.
"""

        messages.append({
            "role": "user",
            "content": current_message
        })

        # Llamar a Claude AI
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="""Eres un asistente legal especializado en el Código Nacional
            de Tránsito de Colombia. Usa el historial de conversación para dar
            respuestas contextuales y coherentes.""",
            messages=messages
        )

        return response.content[0].text
```

**Nuevo endpoint:** `backRag/app/api/v1/endpoints/query.py`

```python
@router.post("/query")
async def query_transit_code(request: QueryRequest):
    """
    Consulta con soporte para historial conversacional
    """
    # Búsqueda en ChromaDB (sin cambios)
    results = search_service.hybrid_search(
        query=request.query,
        max_results=request.max_results
    )

    # Generar respuesta CON historial conversacional
    answer = llm_service.generate_response(
        query=request.query,
        context=results,
        conversation_history=request.conversation_history  # NUEVO
    )

    return QueryResponse(
        answer=answer,
        confidence=confidence_score,
        sources=sources
    )
```

**Actualizar modelo:** `backRag/app/models/query.py`

```python
class QueryRequest(BaseModel):
    query: str
    max_results: int = 3
    confidence_threshold: float = 0.4
    conversation_history: Optional[List[Dict]] = None  # NUEVO
    session_id: Optional[str] = None  # NUEVO
```

---

## 🚀 Despliegue de Redis

### Opción 1: Docker (Recomendado)

**Nuevo archivo:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: transitobot-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  redis_data:
    driver: local
```

**Iniciar:**
```bash
docker-compose up -d redis
```

---

### Opción 2: Instalación Local

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Verificar:**
```bash
redis-cli ping
# Respuesta: PONG
```

---

## 📊 Beneficios de la Arquitectura con Redis

### 1. Memoria Conversacional
- ✅ Respuestas contextuales basadas en conversación previa
- ✅ Usuario puede hacer preguntas de seguimiento
- ✅ "¿Y cuánto cuesta?" → Entiende que se refiere a la multa anterior

### 2. Contexto Compartido RASA ↔ BackRag
- ✅ Si RASA detectó intent "consultar_multas", BackRag lo sabe
- ✅ BackRag puede continuar la conversación donde RASA la dejó
- ✅ Transición transparente entre sistemas

### 3. Performance
- ✅ Cache de respuestas frecuentes: <5ms vs 500ms
- ✅ Reducción de llamadas a Claude AI (ahorro de costos)
- ✅ Reducción de carga en ChromaDB

### 4. Escalabilidad
- ✅ Redis puede manejar miles de sesiones concurrentes
- ✅ Distribución de carga entre múltiples instancias
- ✅ Persistencia de datos (RDB + AOF)

### 5. Analytics
- ✅ Tracking de queries más frecuentes
- ✅ Análisis de patrones de conversación
- ✅ Métricas de satisfacción y uso

---

## 📈 Casos de Uso Mejorados

### Caso 1: Conversación con Seguimiento

**Sin Redis:**
```
Usuario: "¿Cuál es la multa por pico y placa?"
Bot: "La multa es de tipo C..."

Usuario: "¿Y cuánto cuesta?"
Bot: "No entiendo tu consulta" ❌
```

**Con Redis:**
```
Usuario: "¿Cuál es la multa por pico y placa?"
Bot: "La multa es de tipo C, según el Art. 131..."
Redis: Guarda contexto {last_query: "pico_placa", last_article: "131"}

Usuario: "¿Y cuánto cuesta?"
Redis: Recupera contexto → entiende que se refiere a multa tipo C
Bot: "La multa tipo C tiene un valor de..." ✅
```

---

### Caso 2: Cache de Preguntas Frecuentes

**Pregunta frecuente:** "¿Cuál es el número de emergencias?"

**Primera vez:**
- RouterBack → BackRag → ChromaDB → Claude AI
- Tiempo: ~500ms
- Redis: Guarda en cache

**Siguientes veces (próximas 24h):**
- RouterBack → Redis (HIT!)
- Tiempo: <5ms
- Ahorro: 99% de latencia, 100% de costo LLM

---

### Caso 3: Transición RASA → BackRag con Contexto

```
Usuario: "Hola"
RASA: "¡Hola! ¿En qué puedo ayudarte?"
Redis: {last_intent: "greet"}

Usuario: "Quiero saber sobre multas"
RASA: "Claro, ¿qué tipo de multa?"
Redis: {last_intent: "consultar_multas", stage: "gathering_info"}

Usuario: "Específicamente sobre estacionamiento prohibido en zona escolar"
RASA: [] (no tiene respuesta específica)
RouterBack → BackRag con contexto:
  - conversation_history: [...]
  - last_intent: "consultar_multas"
  - entity: "estacionamiento_prohibido"

BackRag con Claude AI: Genera respuesta contextual usando:
  - Historial conversacional
  - Artículos relevantes de ChromaDB
  - Contexto del intent de RASA

Resultado: Respuesta coherente y contextualizada ✅
```

---

## 🔐 Seguridad y Privacidad

### Datos Sensibles
- ❌ No almacenar información personal (nombres, IDs, etc.)
- ✅ Usar session_id anónimos
- ✅ TTL cortos (24h) para datos de usuario
- ✅ Encriptar datos sensibles si es necesario

### Rate Limiting
```python
def check_rate_limit(user_id: str, limit: int = 100) -> bool:
    """Limitar a 100 requests por hora"""
    key = f"rate_limit:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d:%H')}"
    current = redis.incr(key)
    redis.expire(key, 3600)
    return current <= limit
```

---

## 📊 Monitoreo y Métricas

### Dashboard de Redis
```python
def get_redis_stats():
    return {
        "active_sessions": redis.dbsize(),
        "memory_used": redis.info("memory")["used_memory_human"],
        "cache_hit_rate": calculate_hit_rate(),
        "top_queries": redis.zrange("analytics:popular_queries", 0, 9, desc=True, withscores=True)
    }
```

### Logs Enriquecidos
```
[2025-10-30 10:00:00] [Chat] session=abc123 action=cache_hit query="numero emergencias" latency=3ms
[2025-10-30 10:00:15] [Chat] session=abc123 action=rasa_response source=RASA latency=245ms
[2025-10-30 10:00:30] [Chat] session=abc123 action=backrag_response source=BackRag+Claude latency=1200ms context_used=true
```

---

## 🎯 Resumen de Componentes Actualizados

| Componente | Puerto | Cambios con Redis |
|------------|--------|-------------------|
| Frontend | 5173 | Sin cambios (envía session_id) |
| RouterBack | 8080 | ✅ Integración completa con Redis<br>✅ Cache checking<br>✅ Historial management<br>✅ Context sharing |
| RASA | 5005/5055 | ✅ Recibe contexto desde Redis<br>✅ Guarda tracker en Redis |
| BackRag | 8000 | ✅ Recibe historial conversacional<br>✅ Genera respuestas contextuales |
| **Redis** | **6379** | **✅ NUEVO COMPONENTE**<br>✅ Cache layer<br>✅ Session store<br>✅ Conversation memory |
| ChromaDB | - | Sin cambios |
| Claude AI | - | ✅ Recibe historial para contexto |

---

## 🚦 Siguiente Paso: Implementación

### Fase 1: Setup Básico (1-2 días)
1. ✅ Instalar Redis (Docker o local)
2. ✅ Crear `redis_client.py` en RouterBack
3. ✅ Implementar funciones básicas (set/get)
4. ✅ Testing de conexión

### Fase 2: Historial Conversacional (2-3 días)
1. ✅ Implementar almacenamiento de mensajes
2. ✅ Integrar en endpoint `/chat/message`
3. ✅ Pasar historial a BackRag
4. ✅ Testing de conversaciones contextuales

### Fase 3: Cache (1-2 días)
1. ✅ Implementar cache de respuestas
2. ✅ Estrategia de invalidación
3. ✅ Testing de hit/miss

### Fase 4: Analytics (1 día)
1. ✅ Métricas básicas
2. ✅ Dashboard simple
3. ✅ Monitoreo

---

**Última actualización:** 2025-10-30
**Versión:** 2.0 (Propuesta)
**Estado:** 📋 Pendiente de implementación
