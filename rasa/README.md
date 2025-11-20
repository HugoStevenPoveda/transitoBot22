# RASA - Motor Conversacional de Transibot

Sistema de inteligencia conversacional basado en RASA Open Source, especializado en consultas sobre el **Código Nacional de Tránsito Terrestre de Colombia**. Proporciona procesamiento de lenguaje natural (NLU) y gestión de diálogo para el chatbot Transibot.

## Rol en el Sistema Transibot

RASA es el motor conversacional y orquestador de Transibot:

- **NLU (Natural Language Understanding)**: Clasifica intenciones y extrae entidades de mensajes de usuario
- **Gestión de diálogo**: Maneja flujos conversacionales con reglas e historias
- **Orquestación inteligente**: Decide cuándo usar respuestas predefinidas o consultar BackRag
- **Custom actions**: Ejecuta acciones complejas que integran con BackRag API para procesamiento con LLM

### Integración con otros servicios

```
┌──────────────┐
│  RouterBack  │ ──────> Envía mensajes del usuario
│ (Port 8080)  │         y retorna respuestas procesadas
└──────────────┘
        │
        ▼
┌──────────────┐
│     RASA     │ ──────> 1. NLU: Clasifica intent
│ (Port 5005)  │         2. Gestión de diálogo
│              │         3. Decide acción a tomar
└──────┬───────┘
       │
       ├──────> Respuestas directas (reglas simples)
       │
       ▼
┌──────────────┐
│ RASA Actions │ ──────> Ejecuta custom actions
│ (Port 5055)  │         con lógica compleja
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   BackRag    │ ──────> Consulta LLM (Claude) con RAG
│ (Port 8000)  │         usando contexto de conversación
└──────────────┘
```

## Arquitectura del Servicio

### Arquitectura de Capas NLU

```
┌─────────────────────────────────────────────┐
│         MENSAJE DEL USUARIO                  │
│       "Cuánto cuesta una fotomulta"          │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ SpaCy NLP    │      │ Tokenizer    │
│ (es_core_    │      │ (SpaCy)      │
│  news_lg)    │      │              │
└──────┬───────┘      └──────┬───────┘
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ Featurizers  │      │ Regex +      │
│ (Embeddings) │      │ Lexical      │
└──────┬───────┘      └──────┬───────┘
       │                     │
       └──────────┬──────────┘
                  ▼
         ┌──────────────┐
         │ DIET         │ ──────> Intent + Entities
         │ Classifier   │         {intent: "costos_fotomulta",
         │              │          confidence: 0.92}
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐
         │ Fallback     │ ──────> Si confianza < 60%
         │ Classifier   │         activa action_default_fallback
         └──────────────┘
```

### Arquitectura de Gestión de Diálogo

```
┌─────────────────────────────────────────────┐
│          INTENT CLASIFICADO                  │
│      {intent: "costos_fotomulta"}            │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ Rule Policy  │      │ TED Policy   │
│              │      │ (Machine     │
│ 103 rules    │      │  Learning)   │
└──────┬───────┘      └──────┬───────┘
       │                     │
       └──────────┬──────────┘
                  ▼
         ┌──────────────┐
         │ PREDICCIÓN   │ ──────> Selecciona acción
         │ DE ACCIÓN    │         - utter_* (respuesta directa)
         │              │         - action_* (custom action)
         └──────┬───────┘         - action_default_fallback
                │
                ▼
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌──────────────┐    ┌──────────────┐
│ Respuestas   │    │ Custom       │
│ Predefinidas │    │ Actions      │
│ (utter_*)    │    │ (Python)     │
└──────────────┘    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ BackRag API  │
                    │ (Claude LLM) │
                    └──────────────┘
```

## Estructura de Implementación

```
rasa/
├── data/                           # Datos de entrenamiento
│   ├── nlu.yml                     # ⭐ 107 intents con ~1,850 ejemplos
│   ├── rules.yml                   # ⭐ 103 reglas para respuestas directas
│   └── stories.yml                 # ⭐ 51 historias conversacionales
│
├── actions/                        # Custom actions (Python)
│   ├── actions.py                  # ⭐ 4 acciones personalizadas
│   ├── utils/                      # Utilidades para actions
│   │   ├── intent_categorizer.py  # Categorización de intents
│   │   ├── template_renderer.py   # Renderizado de prompts Jinja2
│   │   ├── nlu_loader.py           # Carga de intents desde nlu.yml
│   │   └── responses_loader.py     # Carga de respuestas desde domain.yml
│   └── templates/                  # Templates Jinja2 para prompts
│       ├── consulta.j2             # Template para consultas directas
│       └── fallback.j2             # Template para fallback con categorías
│
├── domain.yml                      # ⭐ Configuración del dominio
│   ├── intents (107)               # Intenciones reconocidas
│   ├── entities (8)                # Entidades extraíbles
│   ├── slots (10)                  # Variables de sesión
│   ├── responses (107 utter_*)    # Respuestas predefinidas
│   ├── actions (5)                 # Custom actions
│   └── forms (1)                   # Formulario para recolección de datos
│
├── config.yml                      # ⭐ Pipeline NLU + Políticas de diálogo
│   ├── pipeline:                   # Procesamiento NLU
│   │   ├── SpacyNLP                # Modelo spaCy español
│   │   ├── SpacyTokenizer          # Tokenización
│   │   ├── SpacyFeaturizer         # Embeddings semánticos
│   │   ├── CountVectorsFeaturizer  # Vectorización n-grams
│   │   ├── DIETClassifier          # Clasificador de intents/entities
│   │   ├── ResponseSelector         # Selector de respuestas FAQ
│   │   └── FallbackClassifier      # Clasificador de fallback (60%)
│   └── policies:                   # Gestión de diálogo
│       ├── MemoizationPolicy       # Memoriza historias exactas
│       ├── RulePolicy              # Aplica reglas definidas
│       ├── UnexpecTEDIntentPolicy  # Predice próximo intent
│       └── TEDPolicy               # Predice próxima acción (ML)
│
├── endpoints.yml                   # ⭐ Configuración de endpoints
│   └── action_endpoint             # URL del servidor de actions
│
├── credentials.yml                 # Credenciales de canales
├── tests/                          # Tests del modelo
├── models/                         # ⭐ Modelos entrenados (.tar.gz)
│   └── 20251119-154152-denim-dove.tar.gz
│
├── Dockerfile                      # ⭐ Multi-stage build
├── requirements.txt                # Dependencias Python
└── README.md
```

## Elementos Importantes del Servicio

### 1. **Pipeline NLU** (`config.yml`)

**Características:**
- ✅ SpaCy (es_core_news_lg) para español avanzado
- ✅ DIETClassifier: Clasificación multitarea (intent + entities)
- ✅ FallbackClassifier: Umbral 60% de confianza
- ✅ ResponseSelector: Para respuestas tipo FAQ
- ✅ Embeddings semánticos + n-grams (híbrido)

**Flujo del Pipeline:**

```python
# 1. Tokenización con spaCy
"Cuánto cuesta una fotomulta" → ["Cuánto", "cuesta", "una", "fotomulta"]

# 2. Embeddings semánticos (captura sinónimos)
"fotomulta" ≈ "multa" ≈ "infracción"

# 3. N-grams (captura patrones)
["Cuánto_cuesta", "cuesta_una", "una_fotomulta"]

# 4. DIETClassifier (clasificación)
{
  "intent": "costos_fotomulta",
  "confidence": 0.92
}

# 5. FallbackClassifier (verifica confianza)
if confidence < 0.60:
    → action_default_fallback
```

**Precisión esperada:**
- Intent Classification: >85%
- Fallback Detection: 60% threshold

### 2. **Dominio** (`domain.yml`)

**Estadísticas:**
- **107 intents**: Desde `saludo` hasta `consultar_prescripcion`
- **8 entities**: `placa`, `cedula`, `nombre`, `email`, `lugar_hechos`, `tipo_vehiculo`, `tipo_infraccion`
- **10 slots**: Variables de sesión para tracking
- **107 responses**: Respuestas predefinidas (`utter_*`)
- **5 custom actions**: Acciones con lógica Python
- **1 form**: `consultar_fotomulta_form` para recolección de datos

**Intents principales:**
```yaml
# Consultas generales
- preguntar_fotomulta
- costos_fotomulta
- plazo_fotomulta
- descuentos_fotomulta
- impugnar_fotomulta

# Consultas avanzadas
- consultar_notificacion
- consultar_suspension_licencia
- consultar_proceso_cobro
- consultar_curso_pedagogico
- consultar_prescripcion

# Flujo de reporte
- consultar_fotomulta (activa form)
- describir_infraccion
- elegir_pagar / elegir_curso / elegir_impugnar
- afirmar / negar (para envío de correo)
```

### 3. **Custom Actions** (`actions/actions.py`)

**4 Acciones Personalizadas que integran con BackRag API:**

#### **ActionConsultarConOpenRouter**
```python
def run(self, dispatcher, tracker, domain):
    """
    Consulta BackRag con contexto completo de conversación.
    Envía: tracking + pregunta + intent + entidades al LLM.
    """
    # 1. Extrae pregunta, intent, entidades, tracking
    # 2. Selecciona template Jinja2 según categoría de intent
    # 3. Renderiza prompt personalizado
    # 4. POST http://backrag:8000/api/v1/anthropic
    # 5. Retorna respuesta del LLM al usuario
```

**Uso:** Para consultas complejas donde el intent tiene buena confianza.

#### **ActionDefaultFallback**
```python
def run(self, dispatcher, tracker, domain):
    """
    Fallback cuando intent tiene baja confianza (<60%).
    Flujo: Intenta OpenRouter → Si falla → Activa BackRag
    """
    # 1. Usa template 'fallback.j2' con todas las categorías de intents
    # 2. Intenta consulta con BackRag API
    # 3. Si falla, retorna mensaje vacío para activar BackRag RAG
```

**Uso:** Para preguntas ambiguas, out_of_scope, o baja confianza.

#### **ActionProcesarInfraccion**
```python
def run(self, dispatcher, tracker, domain):
    """
    Procesa descripción de infracción del usuario.
    Extrae tipo_infraccion y dispara pregunta sobre acción.
    """
    # 1. Extrae entity 'tipo_infraccion'
    # 2. Guarda en slot
    # 3. Pregunta: "¿Quieres pagar, tomar curso o impugnar?"
```

**Uso:** En flujo de reporte de fotomulta (después del form).

#### **ActionEnviarInformacion**
```python
def run(self, dispatcher, tracker, domain):
    """
    Envía información detallada por correo usando tools de BackRag.
    Usa: buscar_articulos_transito + enviar_email
    """
    # 1. Obtiene acción elegida (pagar/curso/impugnar)
    # 2. Construye prompt especializado según acción
    # 3. POST http://backrag:8000/api/v1/anthropic
    #    con use_tools=True
    # 4. BackRag ejecuta:
    #    - buscar_articulos_transito (búsqueda en ChromaDB)
    #    - enviar_email (ApiTool)
    # 5. Usuario recibe correo con artículo + guía
```

**Uso:** Después de que el usuario confirma que quiere recibir información por correo.

**Arquitectura de integración:**

```
RASA Action Server (Port 5055)
        ↓
    POST /api/v1/anthropic
        ↓
    BackRag (Port 8000)
        ↓
    ┌──────────────────┐
    │ AnthropicService │
    │ (Function        │
    │  Calling)        │
    └─────┬────────────┘
          │
    ┌─────┴─────────────────────┐
    │                           │
    ▼                           ▼
buscar_articulos_transito    enviar_email
(ChromaDB RAG)               (ApiTool 8076)
```

### 4. **Datos de Entrenamiento** (`data/`)

**data/nlu.yml** - 107 intents con ejemplos:
```yaml
- intent: costos_fotomulta
  examples: |
    - cuánto cuesta una fotomulta
    - cuál es el valor de una multa por exceso de velocidad
    - qué precio tiene la infracción por celular al conducir
    - quiero saber el monto de las fotomultas
    - precios de las multas de tránsito
```

**data/rules.yml** - 103 reglas (respuestas directas):
```yaml
- rule: Responder a consulta de costos
  steps:
  - intent: costos_fotomulta
  - action: utter_costos_fotomulta
```

**data/stories.yml** - 51 historias (flujos conversacionales):
```yaml
- story: Flujo completo de reporte de fotomulta
  steps:
  - intent: consultar_fotomulta
  - action: consultar_fotomulta_form
  - active_loop: consultar_fotomulta_form
  - active_loop: null
  - slot_was_set:
    - nombre: Juan Pérez
    - email: juan@example.com
  - intent: describir_infraccion
  - action: action_procesar_infraccion
  - intent: elegir_pagar
  - action: action_procesar_eleccion
  - intent: afirmar
  - action: action_enviar_informacion
```

### 5. **Políticas de Diálogo** (`config.yml`)

```yaml
policies:
  # 1. Memoriza conversaciones exactas
  - name: MemoizationPolicy

  # 2. Aplica reglas definidas (alta prioridad)
  - name: RulePolicy
    core_fallback_threshold: 0.6
    core_fallback_action_name: "action_default_fallback"

  # 3. Predice próximo intent (ML)
  - name: UnexpecTEDIntentPolicy
    max_history: 5
    epochs: 100

  # 4. Predice próxima acción (ML)
  - name: TEDPolicy
    max_history: 5
    epochs: 100
```

**Orden de prioridad:**
1. **RulePolicy** → Si hay regla que coincide
2. **MemoizationPolicy** → Si hay historia exacta memorizada
3. **TEDPolicy/UnexpecTEDIntentPolicy** → Predicción por ML

### 6. **Endpoints** (`endpoints.yml`)

```yaml
action_endpoint:
  url: "http://localhost:5055/webhook"
```

**En Docker Compose:**
```yaml
environment:
  - ACTION_SERVER_URL=http://transibot-rasa-actions:5055/webhook
```

### 7. **Dockerfile Multi-Stage**

Optimizado para producción:
- **Stage 1**: Instala dependencias (spaCy + modelo)
- **Stage 2**: Imagen final ligera
- **Modelo externo**: Se monta como volumen (no baked-in)
- Usuario no-root (`appuser`)
- Healthcheck integrado

**Peculiaridad: Modelo como volumen**
```dockerfile
# El modelo NO se incluye en la imagen
# Se monta externamente:
volumes:
  - ./models:/app/models

# Ventajas:
# ✅ Actualizar modelo sin rebuild
# ✅ Entrenar en máquina local, desplegar en servidor
# ✅ Imagen Docker más liviana
```

### 8. **Templates Jinja2 para Prompts** (`actions/templates/`)

**consulta.j2** - Para consultas directas:
```jinja2
Eres un asistente experto en el Código Nacional de Tránsito de Colombia.

INTENT DETECTADO: {{ intent_name }}
CONFIANZA: {{ confidence }}

CONTEXTO DE CONVERSACIÓN:
{{ tracking }}

INSTRUCCIONES:
- Responde de forma corta y concreta
- Usa solo información real del tránsito colombiano
- Mantén coherencia con el historial
```

**fallback.j2** - Para fallback con categorización:
```jinja2
Eres un asistente experto en el Código Nacional de Tránsito de Colombia.

SITUACIÓN: No detecté con claridad la intención del usuario.

PREGUNTA DEL USUARIO: {{ user_question }}

INTENCIONES DISPONIBLES POR CATEGORÍA:
{% for category, intents in categorized_intents.items() %}
{{ category }}:
  {% for intent in intents %}
  - {{ intent }}
  {% endfor %}
{% endfor %}

INSTRUCCIONES:
1. Analiza la pregunta y determina el intent más probable
2. Si ninguno coincide, busca en el Código de Tránsito
3. Responde de forma corta y directa
```

## Flujo de Consulta Completo

### Escenario 1: Consulta directa con alta confianza

```
Usuario: "Cuánto cuesta una fotomulta por exceso de velocidad"
   ↓
RASA NLU Pipeline
   ↓
Intent: costos_fotomulta (confidence: 0.92)
   ↓
RulePolicy: rule "Responder a consulta de costos"
   ↓
Action: utter_costos_fotomulta
   ↓
Bot: "Las fotomultas varían según el tipo de infracción. ¿Quieres saber de alguna específica?"
```

### Escenario 2: Consulta compleja → BackRag con function calling

```
Usuario: "Quiero información sobre cómo impugnar una fotomulta por exceso de velocidad"
   ↓
RASA NLU Pipeline
   ↓
Intent: describir_infraccion (confidence: 0.88)
Entity: tipo_infraccion = "exceso de velocidad"
   ↓
Custom Action: action_procesar_infraccion
   ↓
Bot: "¿Qué te gustaría hacer con esta infracción? (pagar/curso/impugnar)"
   ↓
Usuario: "impugnar"
   ↓
Intent: elegir_impugnar
   ↓
Custom Action: action_procesar_eleccion
   ↓
Bot: "¿Quieres recibir información detallada por correo?"
   ↓
Usuario: "sí"
   ↓
Intent: afirmar
   ↓
Custom Action: action_enviar_informacion
   ↓
POST http://backrag:8000/api/v1/anthropic
{
  "use_tools": true,
  "available_tools": ["buscar_articulos_transito", "enviar_email"],
  "pregunta": "Información sobre impugnar exceso de velocidad"
}
   ↓
BackRag ejecuta:
1. buscar_articulos_transito("exceso de velocidad")
   → Encuentra: Artículo 131 del CNT
2. enviar_email(
     to_email=user_email,
     motivo="Información para impugnar",
     mensaje="Artículo 131 + pasos legales + plazos"
   )
   ↓
ApiTool (Port 8076) envía correo
   ↓
Bot: "✅ Te he enviado información detallada a tu correo con el artículo violado y los pasos para impugnar."
```

### Escenario 3: Fallback → BackRag RAG

```
Usuario: "Qué pasa si mi carro está mal parqueado"
   ↓
RASA NLU Pipeline
   ↓
Intent: nlu_fallback (confidence: 0.45)
   ↓
FallbackClassifier detecta baja confianza
   ↓
Custom Action: action_default_fallback
   ↓
Intenta con template fallback.j2
   ↓
POST http://backrag:8000/api/v1/anthropic
{
  "context": {
    "system": "Template fallback con 107 intents categorizados",
    "user": "Historial de conversación"
  },
  "pregunta": "Qué pasa si mi carro está mal parqueado"
}
   ↓
Si BackRag responde → Bot envía respuesta del LLM
   ↓
Si BackRag falla → Activa BackRag RAG (búsqueda en ChromaDB)
```

## Entrenamiento del Modelo

### Flujo de entrenamiento local

```bash
cd /home/hpoveda/Documents/AppChat/rasa

# 1. Validar datos antes de entrenar
rasa data validate

# 2. Entrenar modelo completo
rasa train

# Salida:
# ✅ Your Rasa model has been saved at:
#    /home/hpoveda/Documents/AppChat/rasa/models/20251119-154152-denim-dove.tar.gz

# 3. Probar en shell
rasa shell --debug

# 4. Evaluar precisión
rasa test nlu --cross-validation
```

### Entrenamientos parciales

```bash
# Solo NLU (más rápido, útil si solo cambió nlu.yml)
rasa train nlu

# Solo diálogo (útil si solo cambiaron rules.yml o stories.yml)
rasa train core
```

### Flujo de despliegue en producción

```bash
# PASO 1: Entrenar modelo localmente
cd rasa
rasa train

# PASO 2: Copiar modelo a carpeta de despliegue
cp models/20251119-154152-denim-dove.tar.gz \
   ../transibot/models/

# PASO 3: Actualizar docker-compose.yml
# environment:
#   - RASA_MODEL_PATH=/app/models/20251119-154152-denim-dove.tar.gz

# PASO 4: Desplegar con Docker
cd ../transibot
docker compose up -d rasa rasa-actions

# PASO 5: Verificar logs
docker compose logs -f rasa
```

**Ventaja:** No necesitas rebuild de la imagen Docker para actualizar el modelo, solo reiniciar el contenedor.

## Uso con Docker

### Construcción de imágenes

```bash
# Imagen del servidor RASA
docker build -t transibot-rasa -f Dockerfile .

# Imagen del servidor de actions
docker build -t transibot-rasa-actions -f actions/Dockerfile .
```

### Con Docker Hub (Transibot)

```bash
# Pull desde Docker Hub
docker pull hugostevenpoveda692/transibot-rasa:latest
docker pull hugostevenpoveda692/transibot-rasa-actions:latest

# Ejecutar (requiere modelo montado como volumen)
docker run -p 5005:5005 \
  -v $(pwd)/models:/app/models \
  -e RASA_MODEL_PATH=/app/models/20251119-154152-denim-dove.tar.gz \
  hugostevenpoveda692/transibot-rasa:latest
```

### Healthcheck

```bash
# RASA server
curl http://localhost:5005/

# Response:
# {"version": "3.x.x", "minimum_compatible_version": "3.0.0"}

# Action server
curl http://localhost:5055/health

# Response:
# {"status": "ok"}
```

## Integración con BackRag

Las custom actions consumen la API de BackRag para procesamiento con LLM.

**Desde RASA Actions:**
```python
import requests

API_BASE_URL = "http://backrag:8000/api"

response = requests.post(
    f"{API_BASE_URL}/v1/anthropic",
    json={
        "context": {
            "system": "Prompt del sistema",
            "user": "Historial de conversación"
        },
        "pregunta": "Pregunta del usuario",
        "entidades": [...],
        "intencion": "intent_name",
        "use_tools": True,  # Opcional: para function calling
        "available_tools": ["buscar_articulos_transito", "enviar_email"]
    },
    timeout=30
)

data = response.json()
answer = data.get("answer", "")
```

**En Docker Compose:**
```yaml
services:
  rasa-actions:
    depends_on:
      - backrag
    environment:
      - API_BASE_URL=http://transibot-backrag:8000/api
```

## Comandos Útiles

### Desarrollo

```bash
# Entrenar todo
rasa train

# Solo NLU
rasa train nlu

# Solo diálogo
rasa train core

# Probar en shell
rasa shell

# Probar con debug
rasa shell --debug

# Validar datos
rasa data validate

# Evaluar modelo
rasa test nlu --cross-validation

# Visualizar historias
rasa visualize
```

### Producción

```bash
# Iniciar servidor RASA
rasa run --enable-api --cors "*" --port 5005

# Iniciar servidor de actions
rasa run actions --port 5055

# Ver logs de Docker
docker compose logs -f rasa
docker compose logs -f rasa-actions

# Reiniciar servicios (después de actualizar modelo)
docker compose restart rasa rasa-actions
```

## Troubleshooting

### Error: "No pre-trained model found"

```bash
# Verificar que existe modelo en host
ls -lh ./models/*.tar.gz

# Si no existe, entrenar
cd rasa
rasa train

# Reiniciar contenedor
docker compose restart rasa
```

### Error: "Action server not reachable"

```bash
# Verificar que action server está corriendo
curl http://localhost:5055/health

# En Docker, verificar conectividad entre servicios
docker compose exec rasa ping rasa-actions

# Revisar logs
docker compose logs -f rasa-actions
```

### Baja precisión en intents

```bash
# Evaluar modelo
rasa test nlu --cross-validation

# Ver matriz de confusión en results/
cat results/intent_confusion_matrix.png

# Agregar más ejemplos a intents con baja precisión en data/nlu.yml
# Reentrenar
rasa train nlu
```

### Error: "Could not connect to BackRag API"

```bash
# Verificar que BackRag está corriendo
curl http://localhost:8000/health

# En Docker, verificar network
docker compose exec rasa-actions ping transibot-backrag

# Revisar logs de BackRag
docker compose logs -f backrag
```

### Modelo desactualizado

```bash
# 1. Entrenar nuevo modelo
cd rasa
rasa train

# 2. Copiar a carpeta de despliegue
cp models/[NUEVO_MODELO].tar.gz ../transibot/models/

# 3. Actualizar RASA_MODEL_PATH en docker-compose.yml

# 4. Reiniciar (NO rebuild)
cd ../transibot
docker compose restart rasa
```

## Estadísticas del Modelo Actual

- **Modelo**: 20251119-154152-denim-dove.tar.gz
- **Tamaño**: ~37 MB
- **Intents**: 107 intents definidos
- **Ejemplos de entrenamiento**: ~1,850 ejemplos
- **Rules**: 103 reglas
- **Stories**: 51 historias conversacionales
- **Responses**: 107 respuestas (utter_*)
- **Entities**: 8 (placa, cedula, nombre, email, lugar_hechos, tipo_vehiculo, tipo_infraccion, etc.)
- **Custom Actions**: 4 acciones con integración BackRag
- **Forms**: 1 formulario (consultar_fotomulta_form)

**Precisión esperada:**
- Intent Classification Accuracy: >85%
- Entity Extraction: Variable según uso
- Dialogue Policy Accuracy: >90% (debido a rules bien definidas)

## Arquitectura de Respuesta Conversacional

RASA implementa una estrategia híbrida:

1. **Respuestas predefinidas (rules)**: Para consultas frecuentes y flujos simples
2. **Consultas con LLM (actions + BackRag)**: Para consultas complejas con contexto
3. **Fallback inteligente**: Cuando la confianza es baja (<60%), usa BackRag con RAG

```
                    ┌─────────────────┐
                    │ Usuario pregunta │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  NLU Pipeline   │
                    │ (DIETClassifier)│
                    └────────┬─────────┘
                             │
                   ┌─────────┴──────────┐
                   │                    │
         confidence >= 60%     confidence < 60%
                   │                    │
                   ▼                    ▼
          ┌────────────────┐   ┌────────────────┐
          │ Rule/Story     │   │ Fallback       │
          │ Match?         │   │ Classifier     │
          └────┬───────────┘   └────────┬───────┘
               │                        │
       ┌───────┴────────┐              │
       │                │              │
       ▼                ▼              ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ utter_*     │  │ action_*     │  │ action_      │
│ (respuesta  │  │ (BackRag API)│  │ default_     │
│  directa)   │  │              │  │ fallback     │
└─────────────┘  └──────────────┘  └──────┬───────┘
                                           │
                                           ▼
                                   ┌──────────────┐
                                   │ BackRag RAG  │
                                   │ (ChromaDB)   │
                                   └──────────────┘
```

## Flujo de Historias Típico

```
Saludo → inicio de interacción
   ↓
Planteamiento del problema → usuario describe situación
   ↓
Consulta específica → solicita explicación sobre infracción o norma
   ↓
Información del asistente → descripción legal, valor, tipo, consecuencias
   ↓
Guía práctica → cómo actuar, pagar, apelar o prevenir
   ↓
Cierre → agradecimiento, confirmación, despedida
```

## Mejoras Futuras

- [ ] Entrenar con más ejemplos de intents con baja precisión
- [ ] Agregar soporte para consulta de RUNT (base de datos oficial)
- [ ] Implementar slots avanzados para tracking de múltiples fotomultas
- [ ] Integrar con API de pagos para permitir pago directo
- [ ] Dashboard de analytics de conversaciones
- [ ] A/B testing de modelos en producción
- [ ] Soporte multicanal (WhatsApp, Telegram)

## Licencia

Parte del sistema Transibot.

---

**Stack Tecnológico:**
- RASA Open Source 3.x
- SpaCy (es_core_news_lg)
- Python 3.11
- DIETClassifier + TEDPolicy
- Jinja2 para templates de prompts
- Docker multi-stage
- Integration con Claude AI (vía BackRag)

**Puertos:**
- 5005: RASA Server (HTTP API)
- 5055: RASA Actions Server (Custom Actions)

**Imágenes Docker:**
- `hugostevenpoveda692/transibot-rasa:latest`
- `hugostevenpoveda692/transibot-rasa-actions:latest`

**Modelo:** Se monta como volumen externo (no baked-in)
