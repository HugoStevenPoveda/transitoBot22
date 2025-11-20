# Transibot - Sistema Inteligente de Consulta de Tránsito

Sistema de chatbot conversacional avanzado basado en **RAG (Retrieval-Augmented Generation)** e **IA conversacional** para consultas sobre el **Código Nacional de Tránsito Terrestre de Colombia**. Combina RASA para NLU, Claude AI para generación de respuestas, ChromaDB para búsqueda vectorial, y una arquitectura de microservicios escalable.

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Componentes Principales](#componentes-principales)
- [Flujo de Datos](#flujo-de-datos)
- [Stack Tecnológico](#stack-tecnológico)
- [Instalación y Despliegue](#instalación-y-despliegue)
- [Uso del Sistema](#uso-del-sistema)
- [Configuración Avanzada](#configuración-avanzada)
- [Troubleshooting](#troubleshooting)
- [Mantenimiento](#mantenimiento)
- [Seguridad](#seguridad)
- [Contribución](#contribución)

---

## 🎯 Descripción General

**Transibot** es un asistente virtual especializado en consultas sobre tránsito y fotomultas en Colombia. El sistema utiliza técnicas avanzadas de procesamiento de lenguaje natural y generación aumentada por recuperación para proporcionar respuestas precisas basadas en el Código Nacional de Tránsito Terrestre.

### Características Principales

✅ **Conversacional Inteligente**: NLU con RASA para clasificación de intenciones (107 intents)
✅ **RAG Avanzado**: Búsqueda híbrida (vectorial + keywords + sinónimos) en ChromaDB
✅ **LLM de Clase Mundial**: Claude 3.5 Sonnet para generación de respuestas contextualizadas
✅ **Function Calling**: Herramientas dinámicas para búsqueda y envío de emails
✅ **Fallback Inteligente**: Estrategia de 5 criterios para garantizar respuestas
✅ **Notificaciones por Email**: Envío automático de información detallada con templates HTML
✅ **Interfaz Moderna**: React + TypeScript con diseño responsive
✅ **Despliegue Simple**: Docker Compose con imágenes pre-construidas en Docker Hub

### Casos de Uso

1. **Consultas sobre fotomultas**: "¿Cuánto cuesta una multa por exceso de velocidad?"
2. **Procedimientos legales**: "¿Cómo impugno una fotomulta?"
3. **Información legal**: "¿Qué dice el artículo 131 del código de tránsito?"
4. **Guía práctica**: "¿Qué documentos debo llevar siempre en mi vehículo?"
5. **Envío de información**: "Envíame por correo los detalles para pagar mi multa"

---

## 🏗️ Arquitectura del Sistema

### Arquitectura General

```
┌───────────────────────────────────────────────────────────────────────────┐
│                            USUARIO FINAL                                   │
│                        (Navegador Web)                                     │
└────────────────────────────────┬──────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                            CAPA DE PRESENTACIÓN                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        FRONTEND (Port 5173)                          │  │
│  │  React 18 + TypeScript + Vite + TailwindCSS                         │  │
│  │  - UI conversacional con historial de chat                          │  │
│  │  - Gestión de sesiones (sender_id)                                  │  │
│  │  - Componentes reutilizables (ChatMessage, ChatInput)               │  │
│  └───────────────────────────┬──────────────────────────────────────────┘  │
└───────────────────────────────┼──────────────────────────────────────────┘
                                │ POST /api/v1/chat/message
                                │ {sender_id, message, metadata}
                                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE ORQUESTACIÓN                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     ROUTERBACK (Port 8080)                           │  │
│  │  FastAPI - API Gateway Inteligente                                  │  │
│  │  ┌────────────────────────────────────────────────────────────────┐ │  │
│  │  │ DECISIÓN INTELIGENTE: ¿RASA o BackRag?                        │ │  │
│  │  │ 5 Criterios de Fallback:                                       │ │  │
│  │  │ 1. Texto vacío                                                 │ │  │
│  │  │ 2. Metadata indica fallback                                    │ │  │
│  │  │ 3. Confianza < 60%                                             │ │  │
│  │  │ 4. Intent out_of_scope/nlu_fallback                           │ │  │
│  │  │ 5. Lista de respuestas vacía                                   │ │  │
│  │  └────────────────────────────────────────────────────────────────┘ │  │
│  └───────────┬──────────────────────────────┬───────────────────────────┘  │
└──────────────┼──────────────────────────────┼──────────────────────────────┘
               │                              │
               │                              │
        ┌──────┴───────┐              ┌──────┴───────────────────────────┐
        │ Ruta RASA    │              │ Ruta BackRag (Fallback)          │
        │ (Respuestas  │              │ (Consultas complejas/ambiguas)   │
        │  directas)   │              │                                  │
        ▼              │              ▼                                  │
┌────────────────────────────────────────────────────────────────────────────┐
│                       CAPA DE PROCESAMIENTO                                 │
│  ┌─────────────────────────────────┐   ┌────────────────────────────────┐  │
│  │      RASA (Ports 5005/5055)     │   │     BACKRAG (Port 8000)        │  │
│  │  Motor Conversacional           │   │  Sistema RAG Avanzado          │  │
│  │  ┌───────────────────────────┐  │   │  ┌──────────────────────────┐  │  │
│  │  │ NLU Pipeline:             │  │   │  │ 1. Embedding de query    │  │  │
│  │  │ - SpaCy (es_core_news_lg) │  │   │  │ 2. Búsqueda híbrida:     │  │  │
│  │  │ - DIETClassifier          │  │   │  │    - Vectorial (cosine)  │  │  │
│  │  │ - FallbackClassifier      │  │   │  │    - Keywords (BM25)     │  │  │
│  │  │   (threshold 60%)         │  │   │  │    - Sinónimos           │  │  │
│  │  └───────────────────────────┘  │   │  │ 3. Reranking con scores  │  │  │
│  │                                  │   │  │ 4. Claude AI LLM         │  │  │
│  │  ┌───────────────────────────┐  │   │  │ 5. Function calling:     │  │  │
│  │  │ Dialogue Management:      │  │   │  │    - search_tool         │  │  │
│  │  │ - RulePolicy (103 rules)  │  │   │  │    - email_tool          │  │  │
│  │  │ - TEDPolicy (ML)          │  │   │  └──────────────────────────┘  │  │
│  │  │ - 51 stories              │  │   │                                 │  │
│  │  └───────────────────────────┘  │   │  ┌──────────────────────────┐  │  │
│  │                                  │   │  │ ChromaDB (Vectorial DB)  │  │  │
│  │  ┌───────────────────────────┐  │   │  │ - 15,248 documentos      │  │  │
│  │  │ Custom Actions:           │  │   │  │ - Embeddings 1024-dim    │  │  │
│  │  │ - consultar_openrouter    │  │   │  │ - Metadata: artículos,   │  │  │
│  │  │ - default_fallback  ──────┼──┼───┼─>│   leyes, tipos           │  │  │
│  │  │ - procesar_infraccion     │  │   │  └──────────────────────────┘  │  │
│  │  │ - enviar_informacion      │  │   │                                 │  │
│  │  └───────────────────────────┘  │   └─────────────────────────────────┘  │
│  └─────────────────────────────────┘                                        │
└────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         CAPA DE SERVICIOS                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      APISTOOL (Port 8076)                            │  │
│  │  Servicio de Envío de Emails                                        │  │
│  │  - SMTP con Gmail (STARTTLS)                                        │  │
│  │  - Templates HTML con Jinja2                                        │  │
│  │  - Endpoint: POST /api/v1/email/send                                │  │
│  │  - Consumido por: BackRag (email_tool)                              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

### Arquitectura de Microservicios

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DOCKER NETWORK: transibot-net                    │
│                                                                          │
│  ┌────────────────┐     ┌────────────────┐     ┌────────────────┐     │
│  │   Frontend     │────▶│  RouterBack    │────▶│     RASA       │     │
│  │  React + Vite  │     │  FastAPI       │     │  Server+Actions│     │
│  │   Port: 5173   │     │  Port: 8080    │     │  5005 / 5055   │     │
│  │   Nginx        │     │  Orchestrator  │     │  NLU + Dialogue│     │
│  └────────────────┘     └────────┬───────┘     └────────────────┘     │
│                                  │                                      │
│                                  │                                      │
│                                  ▼                                      │
│                         ┌────────────────┐                             │
│                         │    BackRag     │                             │
│                         │  FastAPI + RAG │                             │
│                         │   Port: 8000   │                             │
│                         │  Claude AI LLM │                             │
│                         └────────┬───────┘                             │
│                                  │                                      │
│                    ┌─────────────┼─────────────┐                       │
│                    │             │             │                       │
│                    ▼             ▼             ▼                       │
│           ┌────────────┐  ┌──────────┐  ┌──────────┐                  │
│           │  ChromaDB  │  │ ApiTool  │  │ Anthropic│                  │
│           │  Vectores  │  │  Email   │  │   API    │                  │
│           │  (Volume)  │  │ Port:8076│  │ (External)                  │
│           └────────────┘  └──────────┘  └──────────┘                  │
│                                                                          │
│  ┌────────────────┐                                                     │
│  │  RASA Models   │  (Bind Mount: ./models/)                           │
│  │  37 MB .tar.gz │                                                     │
│  └────────────────┘                                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes Principales

### 1. Frontend (Port 5173)

**Tecnologías**: React 18 + TypeScript + Vite + TailwindCSS

**Responsabilidades**:
- Interfaz de usuario conversacional
- Gestión de sesiones con `sender_id` único
- Historial de mensajes en tiempo real
- Integración con RouterBack API

**Características clave**:
- ✅ Componentes reutilizables (`ChatMessage`, `ChatInput`)
- ✅ Estado global con React hooks
- ✅ sessionStorage para persistencia de sender_id
- ✅ Diseño responsive con Tailwind
- ✅ Build optimizado con Vite
- ✅ Servido con Nginx en producción

**Ubicación**: `/frontend/`
**README**: [frontend/README.md](../frontend/README.md)

---

### 2. RouterBack (Port 8080)

**Tecnologías**: FastAPI + Pydantic + httpx

**Responsabilidades**:
- **API Gateway**: Punto de entrada único para el frontend
- **Orquestación inteligente**: Enrutamiento dinámico entre RASA y BackRag
- **Transformación de mensajes**: Conversión entre formatos UI ↔ RASA ↔ BackRag
- **Estrategia de fallback**: Sistema de 5 criterios para activar BackRag

**Estrategia de Fallback (5 Criterios)**:
1. **Texto vacío**: `response.text == ""`
2. **Metadata indica fallback**: `custom.get("fallback") == True`
3. **Confianza baja**: `confidence < 0.6`
4. **Intent específico**: `intent in ["out_of_scope", "nlu_fallback"]`
5. **Lista vacía**: `len(rasa_responses) == 0`

**Flujo de decisión**:
```
Usuario → RouterBack
  ↓
RASA intenta responder
  ↓
¿Cumple algún criterio de fallback?
  ├─ NO → Retorna respuesta de RASA
  └─ SÍ → Activa BackRag RAG
       ↓
  ¿BackRag responde?
    ├─ SÍ → Retorna respuesta RAG
    └─ NO → Respuesta genérica
```

**Ubicación**: `/routerback/`
**README**: [routerback/README.md](../routerback/README.md)

---

### 3. RASA (Ports 5005/5055)

**Tecnologías**: RASA Open Source 3.x + SpaCy + Python

**Responsabilidades**:
- **NLU**: Clasificación de intenciones y extracción de entidades
- **Gestión de diálogo**: Flujos conversacionales con reglas e historias
- **Custom actions**: Integración con BackRag para consultas complejas

**Estadísticas del modelo**:
- 📊 **107 intents** definidos
- 📝 **~1,850 ejemplos** de entrenamiento
- 📏 **103 reglas** para respuestas directas
- 📖 **51 historias** conversacionales
- 🎯 **Precisión esperada**: >85% en clasificación de intents

**Pipeline NLU**:
```
Mensaje → SpaCy Tokenizer → Featurizers → DIETClassifier → FallbackClassifier
                              (Embeddings)                    (threshold: 60%)
```

**Custom Actions**:
1. `ActionConsultarConOpenRouter`: Consultas con contexto a BackRag
2. `ActionDefaultFallback`: Fallback inteligente con templates
3. `ActionProcesarInfraccion`: Procesa reporte de fotomulta
4. `ActionEnviarInformacion`: Envía email con function calling

**Ubicación**: `/rasa/`
**README**: [rasa/README.md](../rasa/README.md)

---

### 4. BackRag (Port 8000)

**Tecnologías**: FastAPI + ChromaDB + Claude 3.5 Sonnet + Anthropic SDK

**Responsabilidades**:
- **RAG (Retrieval-Augmented Generation)**: Búsqueda híbrida + generación con LLM
- **Búsqueda vectorial**: ChromaDB con embeddings de 1024 dimensiones
- **Function calling**: Herramientas dinámicas (search_tool, email_tool)
- **Gestión de prompts**: Templates Jinja2 para contextos especializados

**Arquitectura RAG**:
```
Query del usuario
  ↓
1. Embedding de query (Voyage AI)
  ↓
2. Búsqueda híbrida en ChromaDB:
   - Búsqueda vectorial (cosine similarity)
   - Búsqueda por keywords (BM25)
   - Expansión con sinónimos
  ↓
3. Reranking por scores
  ↓
4. Construcción de contexto
  ↓
5. Claude AI (function calling)
   ├─ Herramienta: buscar_articulos_transito
   └─ Herramienta: enviar_email
  ↓
6. Respuesta generada
```

**ChromaDB**:
- 📚 **15,248 documentos** del Código Nacional de Tránsito
- 🔢 **Embeddings**: 1024 dimensiones (Voyage AI)
- 🏷️ **Metadata**: artículos, leyes, tipos de infracción
- 🔍 **Búsqueda híbrida**: Vectorial + Keywords + Sinónimos

**Function Calling Tools**:
1. **buscar_articulos_transito**: Búsqueda específica en ChromaDB
2. **enviar_email**: Envío de información por correo (integra con ApiTool)

**Ubicación**: `/backRag/`
**README**: [backRag/README.md](../backRag/README.md)

---

### 5. ApiTool (Port 8076)

**Tecnologías**: FastAPI + SMTP + Jinja2

**Responsabilidades**:
- **Envío de emails**: Servicio SMTP con templates HTML
- **Integración con Gmail**: Soporte para app passwords
- **Templates dinámicos**: Renderizado con Jinja2

**Características**:
- ✅ SMTP seguro con STARTTLS
- ✅ Templates HTML profesionales
- ✅ Validación de emails con EmailStr (Pydantic)
- ✅ Consumido por BackRag (email_tool)

**Endpoint principal**:
```
POST /api/v1/email/send
{
  "to_email": "user@example.com",
  "motivo": "Información sobre fotomulta",
  "mensaje": "Contenido HTML..."
}
```

**Ubicación**: `/apistool/`
**README**: [apistool/README.md](../apistool/README.md)

---

## 🔄 Flujo de Datos

### Flujo Completo: Usuario → Respuesta

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PASO 1: Usuario escribe mensaje                                         │
│ Frontend: "¿Cuánto cuesta una multa por exceso de velocidad?"          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ POST /api/v1/chat/message
                             │ {sender_id: "uuid", message: "..."}
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PASO 2: RouterBack recibe y transforma                                  │
│ - Extrae sender_id, message, metadata                                  │
│ - Transforma a formato RASA                                             │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ POST /webhooks/rest/webhook
                             │ {sender: "uuid", message: "..."}
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PASO 3: RASA procesa NLU                                                │
│ - Tokenización con SpaCy                                               │
│ - Featurizers: Embeddings + n-grams                                    │
│ - DIETClassifier: intent="costos_fotomulta", confidence=0.92           │
│ - FallbackClassifier: confidence >= 60% → OK                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PASO 4: RASA selecciona acción                                          │
│ - RulePolicy encuentra regla para "costos_fotomulta"                   │
│ - Acción seleccionada: utter_costos_fotomulta                          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ Response:
                             │ [{"text": "Las fotomultas varían...",
                             │   "custom": {"intent": "costos_fotomulta"}}]
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PASO 5: RouterBack evalúa criterios de fallback                         │
│ ❌ Texto NO vacío                                                       │
│ ❌ NO tiene metadata fallback                                           │
│ ❌ Confianza alta (0.92)                                                │
│ ❌ Intent NO es out_of_scope                                            │
│ ❌ Lista NO vacía                                                       │
│ → Decisión: Usar respuesta de RASA                                     │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ BotResponse
                             │ {sender_id, messages: [...], timestamp}
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PASO 6: Frontend renderiza respuesta                                    │
│ - Crea componente ChatMessage con texto de bot                         │
│ - Actualiza historial de conversación                                   │
│ - Usuario ve: "Las fotomultas varían según el tipo de infracción..."   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Flujo con Fallback a BackRag

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Usuario: "Qué pasa si mi carro está mal parqueado"                     │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ RASA NLU: intent="nlu_fallback", confidence=0.45                        │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ RouterBack evalúa:                                                       │
│ ✅ Confianza baja (0.45 < 0.6) → CUMPLE CRITERIO 3                     │
│ ✅ Intent "nlu_fallback" → CUMPLE CRITERIO 4                           │
│ → Decisión: ACTIVAR BACKRAG                                            │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ POST /api/v1/query
                             │ {query: "...", max_results: 3}
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ BackRag RAG Pipeline:                                                    │
│ 1. Embedding de query → Vector [1024]                                  │
│ 2. Búsqueda híbrida en ChromaDB:                                       │
│    - Vectorial: 10 docs (cosine > 0.4)                                 │
│    - Keywords: 5 docs (BM25)                                            │
│    - Sinónimos: "parqueado" → "estacionado"                            │
│ 3. Reranking: Top 3 documentos                                         │
│    - Artículo 131 (score: 0.87)                                        │
│    - Artículo 132 (score: 0.76)                                        │
│    - Ley 1843 (score: 0.65)                                            │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ BackRag LLM (Claude 3.5 Sonnet):                                        │
│ - Contexto: Top 3 documentos + historial de conversación               │
│ - Prompt: Template especializado para consultas de tránsito            │
│ - Generación: "Según el Artículo 131 del CNT, el parqueo..."          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ Response:
                             │ {answer: "...", confidence: 0.87, sources: [...]}
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ RouterBack transforma a formato UI                                      │
│ - Mensaje principal con respuesta                                       │
│ - Mensaje secundario con fuentes: "📚 Fuentes consultadas:..."         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Frontend renderiza respuesta RAG                                        │
│ - Muestra respuesta detallada                                           │
│ - Incluye fuentes consultadas                                           │
│ - Custom badge: "source: backrag"                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Flujo con Function Calling (Email)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Usuario completa flujo de reporte de fotomulta:                         │
│ 1. Describe infracción: "exceso de velocidad"                          │
│ 2. Elige acción: "impugnar"                                            │
│ 3. Confirma: "sí, quiero recibir información por correo"               │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ RASA Custom Action: action_enviar_informacion                           │
│ - Extrae: accion="impugnar", tipo_infraccion="exceso de velocidad"    │
│ - Construye prompt especializado para impugnación                       │
│ - POST /api/v1/anthropic                                                │
│   {use_tools: true, available_tools: ["buscar_articulos", "email"]}   │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ BackRag Function Calling:                                               │
│                                                                          │
│ LLAMADA 1: buscar_articulos_transito                                    │
│ - Query: "exceso de velocidad artículo violado"                        │
│ - ChromaDB busca y retorna: Artículo 131 del CNT                       │
│                                                                          │
│ LLAMADA 2: enviar_email                                                 │
│ - to_email: user@example.com                                            │
│ - motivo: "Información para impugnar fotomulta"                        │
│ - mensaje: "Artículo 131: [contenido]                                  │
│            Pasos legales: [...]                                         │
│            Plazos: [...]"                                               │
│ - POST http://apistool:8076/api/v1/email/send                          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ApiTool envía email:                                                     │
│ - Carga template HTML: mensaje_generico.html                           │
│ - Renderiza con Jinja2                                                  │
│ - SMTP → Gmail → Usuario recibe email                                  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Usuario ve en frontend:                                                  │
│ "✅ Te he enviado información detallada a tu correo con el artículo    │
│  violado y los pasos para impugnar tu fotomulta."                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Stack Tecnológico

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Utility-first CSS
- **Nginx** - Web server (producción)

### Backend - RouterBack
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **httpx** - Async HTTP client
- **uvicorn** - ASGI server

### AI/ML - RASA
- **RASA Open Source 3.x** - Conversational AI framework
- **SpaCy** (es_core_news_lg) - Spanish NLP
- **DIETClassifier** - Intent classification
- **TEDPolicy** - Dialogue management
- **Python 3.11**

### AI/ML - BackRag
- **FastAPI** - API framework
- **ChromaDB** - Vector database
- **Anthropic Claude 3.5 Sonnet** - LLM
- **Voyage AI** - Embeddings
- **Jinja2** - Template engine

### Services - ApiTool
- **FastAPI** - API framework
- **SMTP (Gmail)** - Email delivery
- **Jinja2** - HTML templates

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy / Web server
- **Python 3.11-slim-bookworm** - Base images

### Databases
- **ChromaDB** - Vector database (15,248 docs)
- **SQLite** (ChromaDB backend) - Metadata storage

---

## 🚀 Instalación y Despliegue

### Requisitos Previos

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4 GB RAM mínimo (8 GB recomendado)
- 10 GB espacio en disco
- Clave API de Anthropic (Claude)
- Credenciales SMTP para Gmail

### Paso 1: Obtener el Código

```bash
git clone https://github.com/tu-usuario/transibot.git
cd transibot
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

**Variables críticas**:
```bash
# Anthropic API (obtener en https://console.anthropic.com/)
ANTHROPIC_API_KEY=sk-ant-api03-...

# SMTP Gmail (usar App Password, no contraseña normal)
SMTP_USER=tugmail@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx

# Opcional: Ajustar puertos si hay conflictos
FRONTEND_PORT=5173
ROUTERBACK_PORT=8080
BACKRAG_PORT=8000
RASA_PORT=5005
APISTOOL_PORT=8076
```

### Paso 3: Verificar Modelo de RASA

El modelo ya está incluido en `./models/`:
```bash
ls -lh ./models/20251119-154152-denim-dove.tar.gz
# Debe mostrar: ~37 MB
```

### Paso 4: Iniciar Servicios

```bash
# Descargar imágenes desde Docker Hub
docker compose pull

# Iniciar todos los servicios
docker compose up -d

# Ver progreso de inicio
docker compose logs -f
```

### Paso 5: Verificar Estado

```bash
# Ver estado de contenedores
docker compose ps

# Todos deben mostrar "healthy" después de ~2 minutos
```

**Salida esperada**:
```
NAME                     STATUS            PORTS
transibot-frontend       Up (healthy)      0.0.0.0:5173->5173/tcp
transibot-routerback     Up (healthy)      0.0.0.0:8080->8080/tcp
transibot-backrag        Up (healthy)      0.0.0.0:8000->8000/tcp
transibot-rasa           Up (healthy)      0.0.0.0:5005->5005/tcp
transibot-rasa-actions   Up (healthy)      0.0.0.0:5055->5055/tcp
transibot-apistool       Up (healthy)      0.0.0.0:8076->8076/tcp
```

### Paso 6: Acceder a la Aplicación

Abrir en navegador:
- **Frontend**: http://localhost:5173

APIs de backend (opcional):
- **RouterBack Docs**: http://localhost:8080/docs
- **BackRag Docs**: http://localhost:8000/api/v1/docs
- **ApiTool Docs**: http://localhost:8076/docs
- **RASA Status**: http://localhost:5005/

---

## 📖 Uso del Sistema

### Ejemplos de Consultas

#### 1. Consulta Simple (RASA)
```
Usuario: "Hola"
Bot: "Hola! Soy tu asistente virtual para consultas sobre tránsito y fotomultas en Colombia. ¿En qué puedo ayudarte?"
```

#### 2. Consulta Directa (RASA)
```
Usuario: "¿Cuánto cuesta una multa por exceso de velocidad?"
Bot: "Las fotomultas por exceso de velocidad varían según la gravedad de la infracción. ¿Quieres saber sobre alguna específica?"
```

#### 3. Consulta Compleja (BackRag RAG)
```
Usuario: "¿Qué pasa si mi carro está mal parqueado frente a un hidrante?"
Bot: "Según el Artículo 131 del Código Nacional de Tránsito Terrestre, estacionar frente a hidrantes, entradas de bomberos o zonas de emergencia está prohibido. La sanción es de 15 SMLDV (aproximadamente $600,000 COP) y puede incluir inmovilización del vehículo..."

📚 Fuentes consultadas:
1. Artículo 131 - Código Nacional de Tránsito
2. Ley 1843 de 2017 - Seguridad vial
```

#### 4. Flujo con Function Calling
```
Usuario: "Quiero información sobre cómo impugnar una fotomulta por exceso de velocidad"
Bot: "Entiendo que recibiste una fotomulta por exceso de velocidad. ¿Qué te gustaría hacer?"
- Pagar
- Tomar curso pedagógico
- Impugnar

Usuario: "Impugnar"
Bot: "¿Quieres recibir información detallada sobre el proceso de impugnación por correo electrónico?"

Usuario: "Sí"
Bot: "✅ Te he enviado información completa a tu correo con:
- El artículo específico violado
- Pasos legales para impugnar
- Documentos necesarios
- Plazos legales
- Formularios requeridos"
```

### Comandos de Gestión

```bash
# Ver logs en tiempo real
docker compose logs -f

# Ver logs de servicio específico
docker compose logs -f backrag
docker compose logs -f rasa

# Reiniciar servicio específico
docker compose restart backrag

# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (⚠️ borra ChromaDB)
docker compose down -v

# Actualizar imágenes desde Docker Hub
docker compose pull
docker compose up -d

# Ver uso de recursos
docker compose stats
```

---

## ⚙️ Configuración Avanzada

### Actualizar Modelo de RASA

```bash
# 1. Entrenar nuevo modelo localmente
cd ../rasa
rasa train

# 2. Copiar modelo a carpeta de despliegue
cp models/NUEVO_MODELO.tar.gz ../transibot/models/

# 3. Actualizar docker-compose.yml o .env
RASA_MODEL_PATH=/app/models/NUEVO_MODELO.tar.gz

# 4. Reiniciar RASA (NO rebuild necesario)
cd ../transibot
docker compose restart rasa rasa-actions
```

### Ajustar Configuración de BackRag

Editar `.env`:
```bash
# Cambiar umbral de confianza para búsqueda
SEARCH_CONFIDENCE_THRESHOLD=0.5

# Ajustar número máximo de resultados
SEARCH_MAX_RESULTS=5

# Timeout para Anthropic API
ANTHROPIC_TIMEOUT=30
```

### Configurar CORS para Producción

Editar `.env`:
```bash
# Desarrollo (permite todo)
CORS_ORIGINS=["*"]

# Producción (solo dominios específicos)
CORS_ORIGINS=["https://transibot.example.com","https://app.transibot.com"]
```

### Escalar Servicios

```bash
# Escalar BackRag para más carga
docker compose up -d --scale backrag=3

# Usar load balancer (nginx, traefik, etc.)
# Configurar en docker-compose.yml
```

---

## 🔧 Troubleshooting

### RASA no inicia (unhealthy)

**Problema**: `docker compose ps` muestra RASA como unhealthy

**Soluciones**:
```bash
# 1. Verificar que existe el modelo
ls -lh ./models/20251119-154152-denim-dove.tar.gz

# 2. Revisar logs
docker compose logs rasa

# 3. RASA requiere tiempo para cargar modelo (~60-120s)
# Esperar 2 minutos y verificar de nuevo
docker compose ps

# 4. Verificar path en docker-compose.yml
# environment:
#   - RASA_MODEL_PATH=/app/models/20251119-154152-denim-dove.tar.gz

# 5. Si persiste, rebuild
docker compose build rasa
docker compose up -d rasa
```

### BackRag no conecta con Anthropic

**Problema**: Error "Invalid API key" o timeout

**Soluciones**:
```bash
# 1. Verificar API key en .env
cat .env | grep ANTHROPIC_API_KEY

# 2. Obtener nueva key en https://console.anthropic.com/

# 3. Actualizar .env y reiniciar
docker compose restart backrag

# 4. Verificar logs
docker compose logs backrag | grep -i "anthropic"

# 5. Probar API key manualmente
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":1024,"messages":[{"role":"user","content":"test"}]}'
```

### ApiTool no envía emails

**Problema**: Emails no llegan o error de autenticación

**Soluciones**:
```bash
# 1. Verificar credenciales SMTP
cat .env | grep SMTP

# 2. Para Gmail, usar App Password (no contraseña normal)
# Ir a: https://myaccount.google.com/apppasswords
# Generar nueva contraseña de aplicación

# 3. Actualizar .env
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # 16 caracteres

# 4. Reiniciar ApiTool
docker compose restart apistool

# 5. Probar endpoint manualmente
curl -X POST http://localhost:8076/api/v1/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "motivo": "Test",
    "mensaje": "Mensaje de prueba"
  }'

# 6. Revisar logs
docker compose logs apistool
```

### Frontend no conecta con backend

**Problema**: Frontend muestra error de conexión

**Soluciones**:
```bash
# 1. Verificar que RouterBack está healthy
docker compose ps routerback

# 2. Verificar puerto en .env
ROUTERBACK_PORT=8080

# 3. Probar API directamente
curl http://localhost:8080/api/v1/health

# 4. Revisar logs de RouterBack
docker compose logs routerback

# 5. Verificar CORS en .env
CORS_ORIGINS=["*"]

# 6. Rebuild frontend si cambió configuración
docker compose build frontend
docker compose up -d frontend
```

### ChromaDB vacía o sin datos

**Problema**: BackRag no encuentra documentos

**Soluciones**:
```bash
# 1. Verificar volumen de ChromaDB
docker volume ls | grep backrag-data

# 2. Ver tamaño del volumen
docker run --rm -v transibot-backrag-data:/data alpine du -sh /data

# 3. Re-indexar documentos (si necesario)
docker compose exec backrag python -c "from app.services.document_loader import load_all_documents; load_all_documents()"

# 4. Verificar cantidad de documentos
curl http://localhost:8000/api/v1/health
# Debe mostrar: "documents_count": 15248
```

### Errores de memoria

**Problema**: Contenedores se reinician por falta de memoria

**Soluciones**:
```bash
# 1. Ver uso de memoria
docker compose stats

# 2. Limitar memoria en docker-compose.yml
services:
  backrag:
    deploy:
      resources:
        limits:
          memory: 2G

# 3. Aumentar memoria de Docker Desktop
# Settings → Resources → Memory → 8 GB

# 4. Limpiar recursos no usados
docker system prune -a
```

---

## 🔒 Seguridad

### Mejores Prácticas

✅ **Variables de entorno**:
- Nunca commitear `.env` a git
- Usar `.env.example` sin credenciales reales
- Rotar API keys regularmente

✅ **Credenciales SMTP**:
- Usar App Passwords de Gmail (no contraseña normal)
- No reutilizar contraseñas entre servicios
- Limitar permisos de la cuenta SMTP

✅ **API Keys**:
- Restringir keys de Anthropic por IP (si es posible)
- Monitorear uso de API en console.anthropic.com
- Configurar límites de rate limiting

✅ **Producción**:
- Cambiar CORS de `["*"]` a dominios específicos
- Usar HTTPS con certificados SSL (Let's Encrypt)
- Implementar authentication en APIs (OAuth, JWT)
- Usar secrets manager (Docker Secrets, Vault)

✅ **Docker**:
- Usar usuario no-root en contenedores (ya configurado)
- Limitar recursos con deploy.resources
- Actualizar imágenes base regularmente

### Checklist de Seguridad

```bash
# ✅ .env no está en git
git ls-files | grep "^\.env$"
# (debe estar vacío)

# ✅ Credenciales son fuertes
# - API key de Anthropic: 64+ caracteres
# - SMTP password: App Password de 16 caracteres

# ✅ CORS configurado para producción
grep CORS_ORIGINS .env
# Producción: CORS_ORIGINS=["https://tu-dominio.com"]

# ✅ Puertos expuestos solo los necesarios
docker compose ps --format "table {{.Service}}\t{{.Ports}}"
```

---

## 🔄 Mantenimiento

### Backup de Datos

```bash
# Crear directorio de backups
mkdir -p backups

# Backup de ChromaDB (named volume)
docker run --rm \
  -v transibot-backrag-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/chromadb-$(date +%Y%m%d).tar.gz /data

# Backup de modelos RASA (bind mount)
cp -r ./models/ ./backups/models-$(date +%Y%m%d)/

# Backup de configuración
cp .env ./backups/.env-$(date +%Y%m%d)
cp docker-compose.yml ./backups/docker-compose-$(date +%Y%m%d).yml
```

### Restaurar Datos

```bash
# Restaurar ChromaDB
docker run --rm \
  -v transibot-backrag-data:/data \
  -v $(pwd)/backups:/backup \
  alpine sh -c "cd /data && tar xzf /backup/chromadb-YYYYMMDD.tar.gz --strip-components=1"

# Reiniciar BackRag
docker compose restart backrag
```

### Actualizar Sistema

```bash
# 1. Backup antes de actualizar
./backup.sh

# 2. Detener servicios
docker compose down

# 3. Actualizar imágenes desde Docker Hub
docker compose pull

# 4. Iniciar con nuevas imágenes
docker compose up -d

# 5. Verificar logs
docker compose logs -f

# 6. Verificar que todos están healthy
docker compose ps
```

### Monitoreo

```bash
# Ver uso de recursos
docker compose stats

# Ver logs en tiempo real
docker compose logs -f

# Healthcheck de todos los servicios
curl http://localhost:8080/api/v1/health
curl http://localhost:8000/api/v1/health
curl http://localhost:8076/health
curl http://localhost:5005/
```

---

## 🤝 Contribución

### Reportar Issues

Para reportar bugs o solicitar features:
1. Ir a: https://github.com/tu-usuario/transibot/issues
2. Usar template de issue
3. Incluir logs y versiones

### Pull Requests

1. Fork del repositorio
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m "Add: nueva funcionalidad"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Desarrollo Local

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/transibot.git

# Desarrollar servicio específico
cd frontend
npm install
npm run dev

cd ../routerback
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📊 Estadísticas del Sistema

- **Total de microservicios**: 5 (Frontend, RouterBack, RASA, BackRag, ApiTool)
- **Total de líneas de código**: ~25,000 líneas
- **Documentos en ChromaDB**: 15,248 documentos
- **Intents de RASA**: 107 intents entrenados
- **Ejemplos de entrenamiento**: ~1,850 ejemplos
- **Reglas conversacionales**: 103 reglas + 51 historias
- **Tamaño total de imágenes Docker**: ~3.5 GB
- **Memoria RAM recomendada**: 8 GB
- **Espacio en disco**: 10 GB mínimo

---

## 📝 Licencia

Parte del sistema Transibot - Proyecto educativo sobre tránsito en Colombia.

---

## 📧 Contacto y Soporte

- **Email**: hugostevenpoveda@gmail.com
- **GitHub**: https://github.com/tu-usuario/transibot
- **Issues**: https://github.com/tu-usuario/transibot/issues

---

## 🎯 Roadmap

### Versión Actual (v1.0)
- ✅ Sistema RAG con ChromaDB
- ✅ Integración con Claude 3.5 Sonnet
- ✅ RASA con 107 intents
- ✅ Function calling (email + búsqueda)
- ✅ Fallback inteligente
- ✅ Docker Compose deployment

### Próximas Versiones

**v1.1** (Corto plazo):
- [ ] Dashboard de analytics
- [ ] Exportar conversaciones a PDF
- [ ] Soporte para WhatsApp
- [ ] Métricas de satisfacción

**v1.2** (Mediano plazo):
- [ ] Autenticación de usuarios
- [ ] Multi-tenancy
- [ ] A/B testing de modelos
- [ ] Cache de respuestas frecuentes

**v2.0** (Largo plazo):
- [ ] Integración con API de RUNT
- [ ] Pagos online de multas
- [ ] Voice assistant (Speech-to-Text)
- [ ] Mobile app (React Native)

---

## 🙏 Agradecimientos

- **Anthropic** por Claude AI
- **RASA** por el framework conversacional
- **ChromaDB** por la base de datos vectorial
- **FastAPI** por el framework web moderno
- **React** por la librería UI

---

**Transibot v1.0** - Sistema Inteligente de Consulta de Tránsito
Desarrollado con ❤️ para Colombia 🇨🇴
