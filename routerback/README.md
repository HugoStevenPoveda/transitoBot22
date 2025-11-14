# RASA Chat Orchestrator

Capa de orquestación FastAPI para comunicación entre UI y RASA.

## Arquitectura

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│     UI      │─────>│  FastAPI         │─────>│    RASA     │
│  (Frontend) │      │  (Orquestador)   │      │  (NLU/Bot)  │
└─────────────┘      └──────────────────┘      └─────────────┘
```

## Características

- Orquestación de mensajes entre UI y RASA
- Transformación de formatos de mensajes
- Gestión de conversaciones
- Health checks
- Documentación automática (Swagger/ReDoc)
- CORS habilitado

## Estructura del Proyecto

```
routerback/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app principal
│   ├── config.py                  # Configuración
│   │
│   ├── api/v1/endpoints/          # Endpoints REST
│   │   ├── chat.py                # Chat endpoints
│   │   └── health.py              # Health checks
│   │
│   ├── core/                      # Lógica central
│   │   ├── rasa_client.py         # Cliente HTTP para RASA
│   │   └── message_transformer.py # Transformación de mensajes
│   │
│   ├── models/                    # Modelos Pydantic
│   │   ├── chat.py                # Modelos UI
│   │   └── rasa.py                # Modelos RASA
│   │
│   └── utils/
│       └── exceptions.py          # Excepciones
│
├── .venv/                         # Entorno virtual (uv)
├── requirements.txt
├── .env
└── README.md
```

## Requisitos Previos

- Python 3.9+
- uv (gestor de paquetes)
- RASA instalado y corriendo

## Instalación

### 1. Crear entorno virtual con uv

```bash
cd routerback
uv venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows
```

### 2. Instalar dependencias

```bash
uv pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y ajusta los valores:

```bash
cp .env.example .env
```

```env
# FastAPI Configuration
APP_NAME=RASA Chat Orchestrator
HOST=0.0.0.0
PORT=8000
DEBUG=true

# RASA Configuration
RASA_URL=http://localhost:5005
RASA_WEBHOOK_PATH=/webhooks/rest/webhook
RASA_TRACKER_PATH=/conversations
RASA_TIMEOUT=30

# CORS
CORS_ORIGINS=["*"]
```

## Ejecutar la Aplicación

### Opción 1: Usando uvicorn directamente

```bash
cd routerback
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Opción 2: Usando el script Python

```bash
cd routerback
python -m app.main
```

La aplicación estará disponible en:
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc

## Endpoints Disponibles

### Health Check

**GET /** - Información básica de la API
```bash
curl http://localhost:8000/
```

**GET /api/v1/health** - Health check
```bash
curl http://localhost:8000/api/v1/health
```

### Chat

**POST /api/v1/chat/message** - Enviar mensaje al bot

```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "user_123",
    "message": "Hola",
    "metadata": {
      "channel": "web"
    }
  }'
```

Respuesta:
```json
{
  "sender_id": "user_123",
  "messages": [
    {
      "text": "Hola! Bienvenido al sistema de consulta de multas de tránsito. ¿En qué puedo ayudarte?",
      "image": null,
      "buttons": null,
      "custom": null
    }
  ],
  "timestamp": "2025-10-16T10:30:00.000Z"
}
```

**GET /api/v1/chat/tracker/{sender_id}** - Obtener estado de conversación

```bash
curl http://localhost:8000/api/v1/chat/tracker/user_123
```

**POST /api/v1/chat/reset/{sender_id}** - Reiniciar conversación

```bash
curl -X POST http://localhost:8000/api/v1/chat/reset/user_123
```

## Ejemplos de Uso con Postman

### 1. Health Check

- **Método**: GET
- **URL**: `http://localhost:8000/api/v1/health`

### 2. Enviar Mensaje Simple

- **Método**: POST
- **URL**: `http://localhost:8000/api/v1/chat/message`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "sender_id": "user_123",
  "message": "Hola"
}
```

### 3. Consultar Multas

- **Método**: POST
- **URL**: `http://localhost:8000/api/v1/chat/message`
- **Body**:
```json
{
  "sender_id": "user_123",
  "message": "Quiero consultar multas"
}
```

### 4. Proporcionar Placa

- **Método**: POST
- **URL**: `http://localhost:8000/api/v1/chat/message`
- **Body**:
```json
{
  "sender_id": "user_123",
  "message": "ABC123"
}
```

### 5. Obtener Estado de Conversación

- **Método**: GET
- **URL**: `http://localhost:8000/api/v1/chat/tracker/user_123`

### 6. Reiniciar Conversación

- **Método**: POST
- **URL**: `http://localhost:8000/api/v1/chat/reset/user_123`

## Flujo de Conversación Completo

```bash
# 1. Saludo inicial
POST /api/v1/chat/message
{
  "sender_id": "user_123",
  "message": "Hola"
}

# 2. Solicitar consulta de multas
POST /api/v1/chat/message
{
  "sender_id": "user_123",
  "message": "Quiero consultar multas"
}

# 3. Proporcionar placa
POST /api/v1/chat/message
{
  "sender_id": "user_123",
  "message": "ABC123"
}

# 4. Ver estado de la conversación
GET /api/v1/chat/tracker/user_123

# 5. Reiniciar si es necesario
POST /api/v1/chat/reset/user_123
```

## Integración con RASA

### Requisitos

1. RASA debe estar corriendo en `http://localhost:5005`
2. El servidor de actions de RASA debe estar en `http://localhost:5055`

### Iniciar RASA

```bash
# Terminal 1: Iniciar servidor RASA
cd TG_CHAT
rasa run --enable-api --cors "*"

# Terminal 2: Iniciar servidor de actions
cd TG_CHAT
rasa run actions

# Terminal 3: Iniciar orquestador FastAPI
cd routerback
uvicorn app.main:app --reload
```

## Modelos de Datos

### UserMessage (Request)
```python
{
    "sender_id": str,      # ID único del usuario
    "message": str,        # Mensaje del usuario
    "metadata": dict       # Metadata adicional (opcional)
}
```

### BotResponse (Response)
```python
{
    "sender_id": str,
    "messages": [
        {
            "text": str,
            "image": str,
            "buttons": list,
            "custom": dict
        }
    ],
    "timestamp": datetime
}
```

## Logs

Los logs se muestran en la consola con el siguiente formato:

```
2025-10-16 10:30:00 - app.api.v1.endpoints.chat - INFO - Recibido mensaje de user_123: Hola
2025-10-16 10:30:01 - app.core.rasa_client - INFO - Enviando mensaje a RASA: sender=user_123, message=Hola
2025-10-16 10:30:02 - app.core.rasa_client - INFO - Respuesta de RASA: 1 mensajes
```

## Solución de Problemas

### RASA no está disponible

**Error**: `"rasa_connected": false` en `/health`

**Solución**:
1. Verifica que RASA esté corriendo: `http://localhost:5005/status`
2. Verifica la configuración en `.env`
3. Revisa los logs de RASA

### Error de CORS

**Error**: CORS policy blocked

**Solución**:
- Ajusta `CORS_ORIGINS` en `.env` con los orígenes permitidos
- Por defecto está configurado como `["*"]` (todos los orígenes)

### Timeout al conectar con RASA

**Error**: Timeout error

**Solución**:
- Incrementa `RASA_TIMEOUT` en `.env` (default: 30 segundos)
- Verifica que RASA Actions esté respondiendo correctamente

## Desarrollo

### Agregar nuevos endpoints

1. Crea un nuevo archivo en `app/api/v1/endpoints/`
2. Define los endpoints con decoradores de FastAPI
3. Registra el router en `app/main.py`

### Agregar validaciones

1. Define nuevos modelos Pydantic en `app/models/`
2. Usa los modelos en los endpoints

## Testing

### Usando curl

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Enviar mensaje
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"sender_id":"test","message":"Hola"}'
```

### Usando HTTPie

```bash
# Health check
http GET http://localhost:8000/api/v1/health

# Enviar mensaje
http POST http://localhost:8000/api/v1/chat/message \
  sender_id=test \
  message="Hola"
```

## Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **Pydantic** - Validación de datos
- **uvicorn** - Servidor ASGI
- **httpx** - Cliente HTTP asíncrono
- **uv** - Gestor de paquetes Python

## Licencia

MIT

## Autor

Desarrollado para el proyecto TG_CHAT
