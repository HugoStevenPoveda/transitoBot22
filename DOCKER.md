# AppChat - Guía de Docker

Esta guía explica cómo ejecutar todo el sistema AppChat usando Docker y Docker Compose.

## Requisitos Previos

- **Docker** 20.10 o superior
- **Docker Compose** 2.0 o superior
- Al menos **8GB de RAM** disponible
- Al menos **10GB de espacio en disco**

Verificar instalación:
```bash
docker --version
docker compose version
```

---

## Configuración Inicial

### 1. Configurar Variables de Entorno

Copia el archivo de ejemplo y configúralo:

```bash
cp .env.docker .env
```

Edita el archivo `.env` y configura tu **ANTHROPIC_API_KEY**:

```env
ANTHROPIC_API_KEY=tu_clave_real_aqui
```

> **IMPORTANTE**: Sin esta clave, el servicio BackRag no funcionará.

### 2. Verificar Estructura de Archivos

Asegúrate de tener esta estructura:

```
AppChat/
├── docker-compose.yml
├── .env
├── frontend/
│   ├── Dockerfile
│   ├── .env.production
│   └── ...
├── routerback/
│   ├── Dockerfile
│   ├── .env.production
│   └── ...
├── backRag/
│   ├── Dockerfile
│   ├── .env.production
│   ├── docker-entrypoint.sh
│   └── data/
├── rasa/
│   ├── Dockerfile
│   ├── .env.production
│   ├── docker-entrypoint.sh
│   └── start-rasa.sh
```

---

## Comandos Principales

### 🚀 Iniciar Todo el Sistema

```bash
docker compose up --build
```

**Opciones útiles:**
- `-d` : Ejecutar en segundo plano (detached)
- `--build` : Forzar rebuild de las imágenes
- `--force-recreate` : Recrear contenedores desde cero

**Ejemplo en background:**
```bash
docker compose up -d --build
```

### 🛑 Detener Todo el Sistema

```bash
docker compose down
```

**Para eliminar también los volúmenes (⚠️ borra datos de ChromaDB):**
```bash
docker compose down -v
```

### 🔄 Reiniciar un Servicio Específico

```bash
# Reiniciar solo el frontend
docker compose restart frontend

# Reiniciar varios servicios
docker compose restart routerback rasa
```

### 📊 Ver Logs

**Logs de todos los servicios:**
```bash
docker compose logs -f
```

**Logs de un servicio específico:**
```bash
docker compose logs -f frontend
docker compose logs -f routerback
docker compose logs -f backrag
docker compose logs -f rasa
```

### 🔍 Ver Estado de los Servicios

```bash
docker compose ps
```

### 🔨 Rebuild de un Servicio Específico

```bash
# Rebuild solo frontend
docker compose build frontend

# Rebuild varios servicios
docker compose build routerback backrag
```

### 🧹 Limpiar Todo (Imágenes, Contenedores, Volúmenes)

```bash
# Detener y eliminar contenedores
docker compose down

# Eliminar imágenes del proyecto
docker compose down --rmi all

# Limpieza completa (⚠️ CUIDADO: elimina todo)
docker compose down -v --rmi all
docker system prune -a
```

---

## Orden de Inicialización

Los servicios se inician en este orden automáticamente:

1. **BackRag** (puerto 8000) - Inicializa ChromaDB
2. **RASA** (puertos 5005, 5055) - Entrena/carga modelo
3. **RouterBack** (puerto 8080) - Espera a BackRag y RASA
4. **Frontend** (puerto 5173) - Espera a RouterBack

Docker Compose usa `depends_on` y `healthcheck` para coordinar el inicio.

---

## Acceso a los Servicios

Una vez iniciado todo, puedes acceder a:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:5173 | Interfaz de usuario |
| **RouterBack** | http://localhost:8080 | API orquestador |
| **RouterBack Docs** | http://localhost:8080/docs | Documentación API |
| **BackRag** | http://localhost:8000 | Sistema RAG |
| **BackRag Docs** | http://localhost:8000/docs | Documentación API |
| **RASA** | http://localhost:5005 | Bot conversacional |
| **RASA Actions** | http://localhost:5055 | Servidor de acciones |

---

## Tiempos de Inicio Esperados

Los primeros builds pueden tardar:

- **Frontend**: 2-3 minutos
- **RouterBack**: 2-3 minutos
- **BackRag**: 5-8 minutos (descarga modelos ML)
- **RASA**: 5-10 minutos (entrenamiento de modelo)

**Total primera vez**: ~15-20 minutos

Inicios posteriores (sin rebuild): ~30-60 segundos

---

## Persistencia de Datos

### Volúmenes Montados

El sistema usa bind mounts para persistir datos:

```yaml
backRag/data/     → /app/data          # ChromaDB y documentos
rasa/models/      → /app/models        # Modelos entrenados de RASA
```

### ¿Qué se Persiste?

✅ Base de datos ChromaDB (BackRag)
✅ Modelos entrenados de RASA
✅ Documentos cargados en BackRag

### ¿Qué NO se Persiste?

❌ Logs de los contenedores (usar `docker compose logs`)
❌ Variables de entorno temporales

---

## Troubleshooting

### 🔴 Error: "ANTHROPIC_API_KEY not set"

**Solución**: Configura la clave en `.env`:
```bash
echo "ANTHROPIC_API_KEY=tu_clave_aqui" > .env
```

### 🔴 Error: Puerto ya en uso

**Problema**: Otro servicio usa el mismo puerto.

**Solución 1** - Cambiar puerto en `docker-compose.yml`:
```yaml
ports:
  - "8080:8080"  # Cambiar primer número: "9090:8080"
```

**Solución 2** - Detener servicio conflictivo:
```bash
# Ver qué usa el puerto
sudo lsof -i :8080
# Matar proceso
kill -9 <PID>
```

### 🔴 Error: "No space left on device"

**Solución**: Limpiar imágenes y contenedores antiguos:
```bash
docker system prune -a
docker volume prune
```

### 🔴 Servicio no inicia (healthcheck failing)

**Ver logs específicos:**
```bash
docker compose logs -f <servicio>
```

**Reiniciar servicio:**
```bash
docker compose restart <servicio>
```

### 🔴 RASA tarda mucho en iniciar

**Normal**: El primer inicio entrena el modelo (~5-10 min).

**Ver progreso:**
```bash
docker compose logs -f rasa
```

### 🔴 BackRag no encuentra ChromaDB

**Verificar volumen:**
```bash
ls -la ./backRag/data/chroma_db/
```

**Reinicializar:**
```bash
docker compose down
rm -rf ./backRag/data/chroma_db
docker compose up -d backrag
```

### 🔴 Frontend no se conecta al backend

**Verificar configuración de red en `.env.production`:**
```bash
cat frontend/.env.production
```

Debe apuntar a `http://routerback:8080` (nombre del servicio).

---

## Comandos Útiles de Desarrollo

### Entrar a un contenedor en ejecución

```bash
# Entrar al contenedor de BackRag
docker compose exec backrag bash

# Entrar al contenedor de RASA
docker compose exec rasa bash
```

### Ejecutar comandos en un contenedor

```bash
# Ver archivos en BackRag
docker compose exec backrag ls -la /app/data

# Verificar modelo de RASA
docker compose exec rasa ls -la /app/models

# Probar conexión desde RouterBack a RASA
docker compose exec routerback curl http://rasa:5005/
```

### Ver uso de recursos

```bash
docker stats
```

### Inspeccionar red

```bash
docker network inspect appchat-network
```

---

## Desarrollo y Actualización de Código

### Actualizar código del Frontend

```bash
# Editar código en ./frontend/src/
# Rebuild y reiniciar
docker compose build frontend
docker compose up -d frontend
```

### Actualizar código de RouterBack

```bash
# Editar código en ./routerback/app/
# Rebuild y reiniciar
docker compose build routerback
docker compose restart routerback
```

### Re-entrenar modelo de RASA

```bash
# Opción 1: Desde el host (si tienes RASA instalado)
cd rasa
rasa train

# Opción 2: Dentro del contenedor
docker compose exec rasa rasa train --fixed-model-name transito_bot

# Reiniciar RASA
docker compose restart rasa
```

### Actualizar documentos en BackRag

```bash
# Agregar documentos en ./backRag/data/documents/
cp nuevo_documento.docx ./backRag/data/documents/

# Re-inicializar base de datos
docker compose exec backrag python scripts/setup_database.py

# O reiniciar el servicio
docker compose restart backrag
```

---

## Producción

### Consideraciones para Producción

1. **Cambiar puertos**: No exponer todos los puertos públicamente
2. **Reverse Proxy**: Usar Nginx/Traefik frente a los servicios
3. **HTTPS**: Configurar certificados SSL
4. **Secrets**: Usar Docker secrets en lugar de .env
5. **Limitar recursos**: Agregar limits de CPU/RAM
6. **Backups**: Automatizar backups de volúmenes
7. **Logging**: Integrar con sistema centralizado (ELK, Loki)

### Ejemplo de límites de recursos

```yaml
services:
  backrag:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## Monitoreo y Salud

### Health Checks

Todos los servicios tienen healthchecks configurados:

```bash
# Ver estado de salud
docker compose ps
```

Salidas posibles:
- `healthy` ✅ - Servicio funcionando correctamente
- `unhealthy` ❌ - Servicio con problemas
- `starting` 🔄 - Servicio iniciando

### Verificar conectividad entre servicios

```bash
# Desde RouterBack, probar RASA
docker compose exec routerback curl http://rasa:5005/

# Desde RouterBack, probar BackRag
docker compose exec routerback curl http://backrag:8000/api/v1/health
```

---

## Backup y Restauración

### Backup de ChromaDB

```bash
# Crear backup
tar -czf backrag-data-backup-$(date +%Y%m%d).tar.gz ./backRag/data/

# Restaurar backup
tar -xzf backrag-data-backup-20250119.tar.gz
docker compose restart backrag
```

### Backup de Modelos RASA

```bash
# Crear backup
tar -czf rasa-models-backup-$(date +%Y%m%d).tar.gz ./rasa/models/

# Restaurar backup
tar -xzf rasa-models-backup-20250119.tar.gz
docker compose restart rasa
```

---

## FAQ

### ¿Cuánto espacio ocupan las imágenes?

```bash
docker images | grep appchat
```

Aproximadamente:
- Frontend: ~30MB
- RouterBack: ~200MB
- BackRag: ~2-3GB
- RASA: ~1.5-2GB

**Total**: ~4-5GB

### ¿Puedo ejecutar solo algunos servicios?

Sí:

```bash
# Solo backend (sin frontend)
docker compose up -d backrag rasa routerback

# Solo RASA para testing
docker compose up -d rasa
```

### ¿Cómo actualizo a una nueva versión?

```bash
# Pull últimos cambios del repo
git pull

# Rebuild todo
docker compose down
docker compose build --no-cache
docker compose up -d
```

### ¿Los datos sobreviven a `docker compose down`?

Sí, los datos en `./backRag/data/` y `./rasa/models/` persisten.

Solo se pierden con `docker compose down -v` (elimina volúmenes).

---

## Soporte

Para problemas o preguntas:

1. Revisa los logs: `docker compose logs -f <servicio>`
2. Verifica healthchecks: `docker compose ps`
3. Revisa la sección Troubleshooting arriba
4. Consulta el README.md principal del proyecto

---

## Resumen de Comandos Rápidos

```bash
# Iniciar todo
docker compose up -d --build

# Ver logs
docker compose logs -f

# Estado de servicios
docker compose ps

# Detener todo
docker compose down

# Reiniciar servicio
docker compose restart <servicio>

# Entrar a contenedor
docker compose exec <servicio> bash

# Limpiar todo
docker compose down -v --rmi all
```
