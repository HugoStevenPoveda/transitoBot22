# Arquitectura del Sistema - TránsitoBot Soacha

## Información General del Proyecto

**Nombre:** TránsitoBot Soacha
**Descripción:** Chatbot inteligente para consultas sobre normas de tránsito enfocado en Soacha, Cundinamarca
**Tipo:** Caso de estudio de implementación de tecnología IA para soluciones municipales
**Estado:** ✅ Completamente operativo

---

## 🏗️ Arquitectura a Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                   │
│                   http://localhost:5173                      │
│                                                               │
│  - Interfaz conversacional moderna                           │
│  - Diseño responsivo con Tailwind CSS                        │
│  - TypeScript para tipado seguro                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              ROUTERBACK (FastAPI - Orquestador)              │
│                   http://localhost:8080                      │
│                                                               │
│  LÓGICA DE FALLBACK:                                         │
│  1. Recibe mensaje del Frontend                              │
│  2. Envía a RASA (bot conversacional)                        │
│  3. Si RASA responde → retorna respuesta                     │
│  4. Si RASA no responde → activa BackRag                     │
│  5. Retorna respuesta al Frontend                            │
└──────────┬─────────────────────────────────┬────────────────┘
           │                                  │
           │ HTTP                             │ HTTP
           ↓                                  ↓
┌──────────────────────┐         ┌───────────────────────────┐
│   RASA (Bot NLU)     │         │  BACKRAG (Sistema RAG)    │
│  http://localhost:   │         │  http://localhost:8000    │
│  - Server: 5005      │         │                           │
│  - Actions: 5055     │         │  ┌─────────────────────┐  │
│                      │         │  │    Claude AI        │  │
│  Intents + Diálogos  │         │  │   (Anthropic API)   │  │
│  predefinidos        │         │  │                     │  │
│                      │         │  │  Generación de      │  │
│                      │         │  │  respuestas         │  │
│                      │         │  │  naturales          │  │
└──────────────────────┘         │  └─────────────────────┘  │
                                 │                           │
                                 │  ┌─────────────────────┐  │
                                 │  │    ChromaDB         │  │
                                 │  │  (Vector Database)  │  │
                                 │  │                     │  │
                                 │  │  - 192 artículos    │  │
                                 │  │  - Embeddings       │  │
                                 │  │  - Búsqueda híbrida │  │
                                 │  └─────────────────────┘  │
                                 └───────────────────────────┘
```

---

## 🔄 Flujo de Comunicación Detallado

### Caso 1: RASA Responde (Conversación Estructurada)

```
Usuario → Frontend → RouterBack → RASA → RouterBack → Frontend → Usuario
```

**Pasos:**
1. Usuario envía mensaje "Hola"
2. Frontend hace POST a RouterBack `/api/v1/chat/message`
3. RouterBack reenvía a RASA `/webhooks/rest/webhook`
4. RASA procesa con NLU y responde
5. RouterBack transforma respuesta
6. Frontend muestra respuesta conversacional

**Log típico:**
```
========== NUEVO MENSAJE ==========
[Chat] Recibido de sender_id=user123: 'Hola'
[Chat] PASO 1: Enviando mensaje a RASA...
[Chat] ✓ RASA respondió con 1 mensaje(s)
[Chat] Respuesta final enviada (origen: RASA)
========== FIN PROCESAMIENTO ==========
```

### Caso 2: RASA No Responde - Activación de BackRag (Búsqueda RAG)

```
Usuario → Frontend → RouterBack → RASA (vacío) → RouterBack → BackRag → RouterBack → Frontend → Usuario
                                                                   ↓
                                                              ChromaDB + Claude AI
```

**Pasos:**
1. Usuario envía consulta compleja sobre código de tránsito
2. RASA no tiene intent definido → respuesta vacía
3. RouterBack detecta fallback y activa BackRag
4. BackRag realiza búsqueda híbrida en ChromaDB:
   - Búsqueda vectorial con embeddings
   - Búsqueda por keywords con sinónimos
5. BackRag envía contexto a Claude AI
6. Claude AI genera respuesta natural con citas legales
7. RouterBack retorna respuesta al Frontend

**Log típico:**
```
[Chat] ✗ RASA no pudo responder (respuesta vacía)
[Chat] PASO 2: Activando fallback a BackRag...
[BackRag] Enviando consulta...
[BackRag] Búsqueda híbrida: 3 resultados encontrados
[BackRag] Claude AI generando respuesta...
[Chat] ✓ BackRag respondió exitosamente
[Chat] Respuesta final enviada (origen: BackRag)
```

---

## 📦 Componentes del Sistema

### 1. Frontend (React + Vite)

**Ubicación:** `/frontend`
**Puerto:** 5173
**URL:** http://localhost:5173

**Stack Tecnológico:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (estilos)
- Lucide React (iconos)

**Responsabilidades:**
- Interfaz de chat conversacional
- Gestión de estado de mensajes
- Comunicación con RouterBack
- Experiencia de usuario responsiva

**Características:**
- Diseño moderno y amigable
- Tiempo real de mensajes
- Indicadores de carga
- Manejo de errores

---

### 2. RouterBack (FastAPI - Orquestador)

**Ubicación:** `/routerback`
**Puerto:** 8080
**URL:** http://localhost:8080
**Docs:** http://localhost:8080/docs

**Stack Tecnológico:**
- FastAPI (framework web)
- Pydantic (validación de datos)
- Uvicorn (servidor ASGI)
- httpx (cliente HTTP asíncrono)

**Estructura:**
```
routerback/
├── app/
│   ├── main.py                    # App principal
│   ├── config.py                  # Configuración
│   ├── api/v1/endpoints/
│   │   ├── chat.py                # Endpoints de chat
│   │   └── health.py              # Health checks
│   ├── core/
│   │   ├── rasa_client.py         # Cliente RASA
│   │   └── message_transformer.py # Transformación
│   └── models/
│       ├── chat.py                # Modelos UI
│       └── rasa.py                # Modelos RASA
```

**Endpoints:**
- `POST /api/v1/chat/message` - Enviar mensaje
- `GET /api/v1/chat/tracker/{sender_id}` - Estado conversación
- `POST /api/v1/chat/reset/{sender_id}` - Reiniciar chat
- `GET /api/v1/health` - Health check

**Variables de Entorno (.env):**
```env
# RASA
RASA_URL=http://localhost:5005
RASA_TIMEOUT=30

# BackRag (Fallback)
BACKRAG_URL=http://localhost:8000
BACKRAG_TIMEOUT=10

# Server
PORT=8080
DEBUG=true
```

---

### 3. RASA (Bot Conversacional)

**Ubicación:** `/rasa`
**Puertos:**
- Servidor RASA: 5005
- Actions Server: 5055

**Stack Tecnológico:**
- RASA Open Source
- NLU (Natural Language Understanding)
- Dialogue Management
- Custom Actions

**Responsabilidades:**
- Procesamiento de lenguaje natural
- Detección de intents
- Gestión de diálogos estructurados
- Ejecución de acciones personalizadas

**Comandos principales:**
```bash
# Entrenar modelo
rasa train

# Servidor principal
rasa run --enable-api --cors "*"

# Servidor de actions
rasa run actions

# Modo interactivo (testing)
rasa shell
```

---

### 4. BackRag (Sistema RAG - Retrieval-Augmented Generation)

**Ubicación:** `/backRag`
**Puerto:** 8000
**URL:** http://localhost:8000
**Docs:** http://localhost:8000/docs

**Stack Tecnológico:**
- FastAPI (framework web)
- ChromaDB (base de datos vectorial)
- SentenceTransformers (embeddings multilingües)
- Claude AI - Anthropic (generación de texto)
- Uvicorn (servidor ASGI)

**Arquitectura por Capas:**
```
backRag/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── query.py               # Endpoint consultas
│   │   └── health.py              # Health checks
│   ├── services/
│   │   ├── llm_service.py         # Claude AI
│   │   ├── search_service.py      # Búsqueda híbrida
│   │   ├── response_service.py    # Generación respuestas
│   │   └── health_service.py      # Status checks
│   ├── repositories/
│   │   └── chroma_repository.py   # ChromaDB
│   ├── core/
│   │   ├── config.py              # Configuración
│   │   ├── dependencies.py        # Inyección dependencias
│   │   └── logging_config.py      # Logs
│   └── models/                    # Modelos Pydantic
├── data/
│   ├── documents/                 # Documentos fuente
│   └── chroma_db/                 # BD vectorial
└── scripts/
    ├── setup_database.py          # Setup ChromaDB
    └── transit_processor.py       # Procesador docs
```

**Endpoints:**
- `POST /api/v1/query` - Consulta código tránsito
- `GET /api/v1/health` - Estado sistema
- `GET /api/v1/stats` - Estadísticas BD
- `GET /api/v1/llm-status` - Estado Claude AI

**Flujo de Consulta RAG:**
```
1. Request → SearchService
2. Búsqueda híbrida en ChromaDB:
   ├─ Búsqueda vectorial (embeddings)
   ├─ Búsqueda por keywords
   └─ Búsqueda por sinónimos
3. Ranking de resultados
4. ResponseService → Claude AI
5. Generación de respuesta natural
6. Formateo con fuentes legales
7. Response → RouterBack
```

**Variables de Entorno (.env):**
```env
ANTHROPIC_API_KEY=sk-ant-...
```

**Base de Datos:**
- **ChromaDB:** Base de datos vectorial
- **Documentos:** 192 artículos del Código Nacional de Tránsito
- **Embeddings:** Modelo multilingüe español
- **Búsqueda:** Híbrida (semántica + keywords)

**Ejemplo de Respuesta:**
```json
{
  "answer": "Según el Artículo 131 del Código Nacional de Tránsito...",
  "confidence": 0.85,
  "sources": [
    {
      "article": "Artículo 131",
      "law": "Ley 769 de 2002 - Código Nacional de Tránsito Terrestre",
      "description": "Restricciones a la circulación",
      "similarity_score": 0.92,
      "content_snippet": "Los vehículos automotores no podrán circular..."
    }
  ],
  "processing_time": 0.45
}
```

---

## 🔧 Resumen de Puertos y URLs

| Servicio       | Puerto | URL Principal              | Documentación              |
|----------------|--------|----------------------------|----------------------------|
| Frontend       | 5173   | http://localhost:5173      | -                          |
| RouterBack     | 8080   | http://localhost:8080      | /docs, /redoc              |
| BackRag        | 8000   | http://localhost:8000      | /docs, /redoc              |
| RASA Server    | 5005   | http://localhost:5005      | /docs                      |
| RASA Actions   | 5055   | http://localhost:5055      | -                          |

---

## ⚙️ Orden de Ejecución Recomendado

Para iniciar el sistema completo, ejecutar en este orden:

### 1. BackRag (Sistema RAG)
```bash
cd backRag
uv run run.py
# o
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. RASA (Bot Conversacional)
```bash
# Terminal 1: Servidor RASA
cd rasa
rasa run --enable-api --cors "*"

# Terminal 2: Actions Server
cd rasa
rasa run actions
```

### 3. RouterBack (Orquestador)
```bash
cd routerback
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
# o
python -m app.main
```

### 4. Frontend (Interfaz Web)
```bash
cd frontend
npm run dev
```

---

## 🔍 Verificación de Servicios

### Health Checks

**RouterBack:**
```bash
curl http://localhost:8080/health
```

**BackRag:**
```bash
curl http://localhost:8000/api/v1/health
```

**RASA:**
```bash
curl http://localhost:5005/
```

**Frontend:**
```bash
# Abrir navegador
http://localhost:5173
```

---

## 🎯 Caso de Uso: Soacha, Cundinamarca

**¿Por qué Soacha?**
- 🏙️ Municipio en crecimiento con necesidades tecnológicas
- 🚦 Desafíos de tránsito típicos de ciudades intermedias
- 💡 Oportunidad de innovación en gobierno digital
- 📊 Modelo replicable para otros municipios colombianos

**Objetivos:**
- Demostrar implementación de IA en gobierno local
- Mejorar acceso ciudadano a información de tránsito
- Reducir consultas presenciales en oficinas municipales
- Crear modelo escalable para otros municipios

---

## 🚀 Características Principales del Sistema

### Arquitectura Híbrida
- ✅ Bot conversacional estructurado (RASA)
- ✅ Sistema RAG generativo (BackRag + Claude AI)
- ✅ Fallback automático e inteligente
- ✅ Respuestas con fuentes legales verificables

### Capacidades
- 🔍 Búsqueda semántica con embeddings
- 💬 Respuestas naturales generadas por IA
- 📚 192 artículos del Código de Tránsito procesados
- 🎯 Búsqueda híbrida (vectorial + keywords + sinónimos)
- ⚡ Respuesta en <1 segundo
- 📊 Precisión >80% en consultas comunes

---

## 📊 Rendimiento

- **Base de Datos:** 192 artículos procesados
- **Tiempo de Búsqueda:** <1 segundo
- **Precisión:** >80% en consultas comunes
- **Embeddings:** Optimizados para español
- **Arquitectura:** Escalable y modular

---

## 🛠️ Tecnologías Resumidas por Categoría

### Frontend
- React 18, TypeScript, Vite, Tailwind CSS

### Backend Orquestador
- FastAPI, Pydantic, Uvicorn, httpx

### Bot Conversacional
- RASA Open Source, NLU, Dialogue Management

### Sistema RAG
- FastAPI, ChromaDB, SentenceTransformers, Claude AI (Anthropic)

### Gestión de Dependencias
- npm (Frontend)
- pip + uv (Backend)

### Base de Datos
- ChromaDB (vectorial)

### IA/ML
- Claude AI (Anthropic) - Generación de texto
- SentenceTransformers - Embeddings multilingües
- RASA NLU - Procesamiento de lenguaje

---

## 📝 Próximas Mejoras

- [ ] Caché de consultas frecuentes con Redis
- [ ] Métricas y analytics con Prometheus
- [ ] Interfaz de administración
- [ ] API de feedback de usuarios
- [ ] Soporte para más documentos legales
- [ ] Deployment con Docker
- [ ] Tests automatizados
- [ ] CI/CD pipeline

---

## 🎓 Proyecto Académico

**Institución:** Pontificia Universidad Javeriana
**Autores:** Oscar Javier, Hugo P, Marc Donald
**Tipo:** Proyecto de grado - Caso de estudio

**Demuestra:**
- ✅ Arquitectura full-stack moderna
- ✅ Procesamiento de documentos legales con IA
- ✅ Búsqueda semántica con embeddings
- ✅ Interfaz conversacional intuitiva
- ✅ Integración de tecnologías emergentes
- ✅ Aplicación práctica de Machine Learning

---

**Última actualización:** 2025-10-30
**Versión:** 1.0.0
