# AppChat - Sistema de Chat con Fallback RAG

Sistema de chat conversacional que integra RASA con fallback automático a un servicio RAG para consultas sobre el Código de Tránsito de Colombia.

## Arquitectura

```
Frontend (React + Vite)
    ↓
RouterBack (FastAPI) - Orquestador
    ↓
    ├─→ RASA (Bot conversacional)
    └─→ BackRag (Sistema RAG fallback) ← Si RASA no puede responder
```

---

## Requisitos Previos

- **Node.js** (para Frontend)
- **Python 3.10+** con `uv` instalado
- **RASA** instalado globalmente o en entorno virtual

---

## Guía Rápida de Ejecución

### 1️⃣ Frontend (React + Vite)

```bash
cd frontend
npm run dev
```

**URL:** http://localhost:5173

---

### 2️⃣ BackRag (Servicio RAG)

```bash
cd backRag
uv run run.py
```

**Puerto:** 8000
**API Docs:** http://localhost:8000/docs

**Nota:** Asegúrate de que la base de datos ChromaDB esté inicializada. Si no lo está, ejecuta primero:
```bash
cd backRag
uv run scripts/setup_database.py
```

---

### 3️⃣ RASA (Bot Conversacional)

**Terminal 1 - Servidor RASA:**
```bash
cd rasa
rasa run --enable-api --cors "*"
```

**Puerto:** 5005

**Terminal 2 - Actions Server (si tienes custom actions):**
```bash
cd rasa
rasa run actions
```

**Puerto:** 5055

**Nota:** Si es la primera vez que ejecutas RASA, primero entrena el modelo:
```bash
cd rasa
rasa train
```

---

### 4️⃣ RouterBack (Orquestador FastAPI)

```bash
cd routerback
python -m app.main
```

**O con uvicorn directamente:**
```bash
cd routerback
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

**Puerto:** 8080
**API Docs:** http://localhost:8080/docs

---

## Resumen de Puertos

| Servicio    | Puerto | URL                          |
|-------------|--------|------------------------------|
| Frontend    | 5173   | http://localhost:5173        |
| RouterBack  | 8080   | http://localhost:8080        |
| BackRag     | 8000   | http://localhost:8000        |
| RASA        | 5005   | http://localhost:5005        |
| RASA Actions| 5055   | http://localhost:5055        |

---

## Orden de Ejecución Recomendado

Ejecuta los servicios en este orden:

1. **BackRag** (primero, para que esté disponible como fallback)
2. **RASA** (servidor principal + actions si aplica)
3. **RouterBack** (orquestador que conecta todo)
4. **Frontend** (interfaz de usuario)

---

## Verificación de Servicios

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

---

## Configuración de Variables de Entorno

### RouterBack - `.env`

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

### BackRag - `.env`

```env
ANTHROPIC_API_KEY=tu_api_key_aqui
```

---

## Flujo de Funcionamiento

1. Usuario envía mensaje desde el **Frontend**
2. **RouterBack** recibe el mensaje y lo envía a **RASA**
3. Si **RASA** responde → Usuario recibe respuesta de RASA
4. Si **RASA no responde** (lista vacía) → **RouterBack** envía consulta a **BackRag**
5. **BackRag** busca en su base de conocimiento y genera respuesta con IA
6. Usuario recibe la respuesta (sin saber de dónde vino)

---

## Comandos Útiles RASA

**Entrenar modelo:**
```bash
cd rasa
rasa train
```

**Modo interactivo (testing):**
```bash
cd rasa
rasa shell
```

**Validar configuración:**
```bash
cd rasa
rasa data validate
```

---

## Troubleshooting

### Error: "RASA no disponible"
- Verifica que RASA esté corriendo en puerto 5005
- Revisa logs de RASA para errores

### Error: "BackRag no disponible"
- Verifica que BackRag esté en puerto 8000
- Asegúrate de que ChromaDB esté inicializado
- Verifica que tengas `ANTHROPIC_API_KEY` configurada

### Error: "RouterBack no puede conectarse"
- Verifica que las URLs en `routerback/.env` sean correctas
- Revisa los logs de RouterBack para más detalles

---

## Logs de Trazabilidad

RouterBack genera logs detallados en cada paso:

```
========== NUEVO MENSAJE ==========
[Chat] Recibido de sender_id=user123: 'mensaje'
[Chat] PASO 1: Enviando mensaje a RASA...
[Chat] ✓ RASA respondió con 1 mensaje(s)
[Chat] Respuesta final enviada (origen: RASA)
========== FIN PROCESAMIENTO ==========
```

Si RASA no responde, verás:
```
[Chat] ✗ RASA no pudo responder (respuesta vacía)
[Chat] PASO 2: Activando fallback a BackRag...
[BackRag] Enviando consulta...
[Chat] ✓ BackRag respondió exitosamente
[Chat] Respuesta final enviada (origen: BackRag)
```

---

## Desarrollo

### Instalar dependencias

**Frontend:**
```bash
cd frontend
npm install
```

**RouterBack:**
```bash
cd routerback
pip install -r requirements.txt
```

**BackRag:**
```bash
cd backRag
uv sync
```

**RASA:**
```bash
cd rasa
pip install -r requirements.txt
```

---

## Documentación de APIs

- **RouterBack:** http://localhost:8080/docs
- **BackRag:** http://localhost:8000/docs
- **RASA:** http://localhost:5005/docs

---

## Contacto y Soporte

Para problemas o preguntas, revisa los logs de cada servicio para identificar el punto de fallo. cada repo independiete.