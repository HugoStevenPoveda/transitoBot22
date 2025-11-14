# TránsitoBot Soacha - Caso de Estudio de Innovación Municipal 🚦🤖

Un chatbot inteligente para consultas sobre normas de tránsito enfocado en Soacha, Cundinamarca. Caso de estudio de implementación de tecnología IA para soluciones municipales.

## 🎯 Estado del Proyecto - FUNCIONANDO ✅

**🚀 PROYECTO COMPLETAMENTE OPERATIVO:**

✅ **Frontend React** - Interfaz moderna y responsiva  
✅ **Backend FastAPI** - API REST completamente funcional  
✅ **ChromaDB** - 192 artículos del Código de Tránsito procesados  
✅ **Búsqueda híbrida** - Vectorial + palabras clave + sinónimos  
✅ **Integración completa** - Frontend ↔ Backend funcionando  
✅ **Respuestas contextuales** - Con fuentes verificables del código  
✅ **Interfaz optimizada** - UX mejorada con metadatos de confianza  
🎯 **Caso de estudio** - Enfocado en necesidades del municipio de Soacha
🔄 **Próximo:** Integración LLM para respuestas más naturales

## 🏛️ Caso de Estudio: Soacha, Cundinamarca

**¿Por qué Soacha?**
- 🏙️ **Municipio en crecimiento** con necesidades tecnológicas
- 🚦 **Desafíos de tránsito** típicos de ciudades intermedias
- 💡 **Oportunidad de innovación** en gobierno digital
- 📊 **Modelo replicable** para otros municipios colombianos

**Objetivos del caso de estudio:**
- Demostrar implementación de IA en gobierno local
- Mejorar acceso ciudadano a información de tránsito
- Reducir consultas presenciales en oficinas municipales
- Crear modelo escalable para otros municipios

## 🚀 Características

- **Frontend moderno** con React 18 + TypeScript
- **Diseño responsivo** con Tailwind CSS
- **API REST** con FastAPI y documentación automática
- **Búsqueda vectorial** con ChromaDB y embeddings multilingües
- **Interfaz conversacional** intuitiva y amigable
- **Citas legales** con fuentes verificables del Código de Tránsito
- **Búsqueda inteligente** con IA y procesamiento de lenguaje natural

## 🛠️ Stack Tecnológico

### Frontend
- React 18 + TypeScript
- Tailwind CSS
- Vite
- Lucide React (iconos)

### Backend
- FastAPI (Python)
- ChromaDB (base de datos vectorial)
- SentenceTransformers (embeddings multilingües)
- Uvicorn (servidor ASGI)

## 📦 Instalación

### Prerrequisitos
- Node.js 16+
- Python 3.8+
- 4GB+ RAM (para modelos de embeddings)

### 1. Clonar el repositorio
```bash
git clone https://github.com/osjav2/transito-chatbot.git
cd transito-chatbot
```

### 2. Configurar Frontend
```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
```

### 3. Configurar Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# IMPORTANTE: Colocar el archivo CodigoNacionaldeTransitoTerrestre.docx en la carpeta backend/

# Configurar ChromaDB (SOLO LA PRIMERA VEZ)
python setup_chromadb.py
```

## 🚀 Inicio Rápido

### 1. Ejecutar Backend
```bash
cd backend
source venv/bin/activate  # Activar entorno virtual
python -m uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Ejecutar Frontend (nueva terminal)
```bash
npm run dev
```

### 3. Usar la aplicación
- **🎨 Chatbot:** http://localhost:5173/
- **📚 API Docs:** http://localhost:8000/docs
- **❤️ Health Check:** http://localhost:8000/api/v1/health

## 🧠 Cómo Funciona

1. **Procesamiento:** El código de tránsito se procesa y segmenta por artículos
2. **Vectorización:** Se generan embeddings multilingües para cada artículo
3. **Búsqueda híbrida:** Combina búsqueda vectorial + palabras clave + sinónimos
4. **Respuesta contextual:** Genera respuestas basadas en artículos relevantes
5. **Interfaz amigable:** Presenta la información de forma conversacional

## 📊 Rendimiento

- **192 artículos** procesados del Código Nacional de Tránsito
- **Búsqueda en <1 segundo** con ChromaDB
- **Precisión >80%** en consultas comunes
- **Soporte multilingüe** con embeddings optimizados para español

## 🏗️ Arquitectura del Proyecto

```
transito-chatbot/
├── src/                    # Frontend React
│   ├── components/         # Componentes React
│   ├── services/          # Servicios de API
│   ├── types/             # Tipos TypeScript
│   └── data/              # Datos mock
├── backend/               # Backend FastAPI
│   ├── fastapi_server.py  # Servidor principal
│   ├── setup_chromadb.py  # Configuración de BD
│   ├── transit_processor.py # Procesador de documentos
│   ├── debug_chromadb.py  # Herramientas de debug
│   └── chroma_db/         # Base de datos (generada)
├── public/                # Archivos estáticos
└── PERSONALIZACION.md     # Guía de personalización
```

## 🔧 API Endpoints

```
GET  /                     # Información básica
GET  /api/v1/health       # Estado del sistema  
POST /api/v1/query        # Consultar código de tránsito
GET  /api/v1/stats        # Estadísticas de la BD
GET  /docs                # Documentación interactiva
```

### Ejemplo de Consulta

```bash
POST /api/v1/query
{
  "query": "¿Cuál es la multa por pico y placa?",
  "max_results": 3,
  "confidence_threshold": 0.4
}
```

### Respuesta Esperada

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

## 🧪 Testing y Debug

```bash
# Verificar estado de la base de datos
cd backend && python debug_chromadb.py

# Probar API directamente
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "límites de velocidad en la ciudad"}'

# Ver estadísticas
curl http://localhost:8000/api/v1/stats
```

## 🎨 Personalización

Ver el archivo [PERSONALIZACION.md](PERSONALIZACION.md) para guías detalladas sobre:
- Cambiar colores y temas
- Agregar nuevas preguntas frecuentes
- Modificar respuestas
- Personalizar la interfaz

## 🚀 Deployment

### Frontend
```bash
npm run build
npm run preview
```

### Backend
```bash
# Producción con Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker fastapi_server:app
```

## 🐛 Solución de Problemas

### Backend no encuentra artículos
```bash
cd backend && python debug_chromadb.py
```

### Error de conexión frontend-backend
- Verificar que FastAPI esté en puerto 8000
- Verificar CORS en `fastapi_server.py`
- Revisar variables de entorno en `.env`

### Problemas con embeddings
- Verificar que el modelo se descargue correctamente
- Liberar memoria: reiniciar el servidor
- Verificar espacio en disco (modelos ocupan ~500MB)

## 📝 Comandos Útiles

```bash
# Frontend
npm run dev      # Servidor de desarrollo
npm run build    # Construir para producción
npm run preview  # Vista previa

# Backend  
python setup_chromadb.py           # Configurar BD
python -m uvicorn fastapi_server:app --reload  # Servidor dev
python debug_chromadb.py           # Diagnosticar
```

## 📈 Próximas Mejoras

- [ ] Integración con LLM (GPT/Claude) para respuestas más naturales
- [ ] Caché de consultas frecuentes con Redis
- [ ] Métricas y analytics con Prometheus
- [ ] Interfaz de administración
- [ ] API de feedback de usuarios
- [ ] Soporte para más documentos legales
- [ ] Deployment con Docker
- [ ] Tests automatizados

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🎓 Proyecto Académico

Este proyecto de grado demuestra:
- ✅ **Arquitectura full-stack moderna**
- ✅ **Procesamiento de documentos legales con IA**
- ✅ **Búsqueda semántica con embeddings**
- ✅ **Interfaz conversacional intuitiva**
- ✅ **Integración de tecnologías emergentes**
- ✅ **Aplicación práctica de Machine Learning**

## 👥 Autores

- **Oscar Javier - Hugo P - Marc Donald** - *Desarrollo Full Stack* - [osjav2](https://github.com/osjav2)

## 🙏 Agradecimientos

- Pontificia Universidad Javeriana
- Código Nacional de Tránsito Terrestre de Colombia
- Comunidad open source de FastAPI y React

---

Desarrollado con ❤️ para el proyecto de grado - **TránsitoBot Colombia** 🇨🇴
