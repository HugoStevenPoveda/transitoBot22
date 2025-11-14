# Rasa Chatbot - Codigo Nacional de Transito

Chatbot educativo sobre normas de transito en Colombia basado en el Codigo Nacional de Transito Terrestre.

## Estructura del Proyecto

```
rasa/
├── data/
│   ├── nlu.yml          # 107 intents con ~1,850 ejemplos de entrenamiento
│   ├── rules.yml        # 103 reglas para respuestas directas
│   └── stories.yml      # 51 historias conversacionales
├── domain.yml           # Configuracion del dominio (intents, entities, responses, actions)
├── config.yml           # Pipeline de NLU y politicas de dialogo
├── endpoints.yml        # Configuracion de endpoints (action server, tracker store)
└── credentials.yml      # Credenciales para canales de comunicacion
```

## Requisitos Previos

```bash
# Instalar Rasa
pip install rasa

# Verificar instalacion
rasa --version
```

## Comandos de Entrenamiento

### 1. Entrenar el modelo completo (NLU + Dialogue)

```bash
cd /home/hpoveda/Documents/AppChat/rasa
rasa train
```

Este comando entrenara tanto el modelo de NLU (comprension del lenguaje) como el modelo de dialogo, generando un archivo en `models/` con timestamp.

### 2. Entrenar solo NLU (mas rapido)

```bash
rasa train nlu
```

Util cuando solo has modificado `data/nlu.yml` y no necesitas reentrenar el modelo de dialogo.

### 3. Entrenar solo el modelo de dialogo

```bash
rasa train core
```

Util cuando solo has modificado `data/stories.yml` o `data/rules.yml`.

### 4. Entrenar con modo debug (ver mas informacion)

```bash
rasa train --debug
```

### 5. Entrenar con configuracion especifica

```bash
rasa train --config config.yml --domain domain.yml --data data/
```

## Comandos de Prueba

### 1. Probar en modo interactivo (shell)

```bash
rasa shell
```

Esto abre una consola interactiva donde puedes chatear con el bot. Ejemplos de preguntas:
- "hola"
- "que tipos de multas existen"
- "cuanto cuesta la multa por exceso de velocidad"
- "como saco mi licencia de conducir"
- "que documentos debo llevar siempre"

Presiona `Ctrl+C` para salir.

### 2. Probar con modo debug (ver intents y confianza)

```bash
rasa shell --debug
```

Muestra informacion detallada sobre:
- Intent detectado y su confianza
- Entities extraidas
- Politica de dialogo utilizada
- Accion seleccionada

### 3. Probar solo NLU (sin dialogo)

```bash
rasa shell nlu
```

Solo muestra la clasificacion de intents sin ejecutar acciones. Util para validar que los intents se estan detectando correctamente.

### 4. Iniciar servidor de Rasa (para integracion)

```bash
rasa run
```

Inicia el servidor en `http://localhost:5005` para recibir peticiones HTTP.

### 5. Iniciar servidor con API habilitada

```bash
rasa run --enable-api --cors "*"
```

Permite llamadas desde cualquier origen (util para desarrollo frontend).

### 6. Iniciar servidor de acciones (si tienes custom actions)

```bash
rasa run actions
```

Inicia el action server en `http://localhost:5055`.

## Validacion de Datos

### 1. Validar todos los archivos de configuracion

```bash
rasa data validate
```

Verifica:
- Consistencia entre `domain.yml`, `nlu.yml`, `rules.yml` y `stories.yml`
- Intents declarados en domain pero no usados en training data
- Responses usadas pero no declaradas
- Conflictos en las stories

### 2. Validar solo stories

```bash
rasa data validate stories
```

## Evaluacion del Modelo

### 1. Evaluar NLU con cross-validation

```bash
rasa test nlu --cross-validation
```

Evalua la precision del modelo NLU usando validacion cruzada (k-folds).

### 2. Evaluar NLU con datos de prueba separados

```bash
rasa test nlu --nlu data/test_nlu.yml
```

### 3. Evaluar el modelo de dialogo

```bash
rasa test core --stories data/test_stories.yml
```

### 4. Generar matriz de confusion de intents

```bash
rasa test nlu --nlu data/nlu.yml --cross-validation --runs 3 --folds 5
```

Los resultados se guardan en `results/`.

## Visualizacion

### 1. Visualizar historias como grafo

```bash
rasa visualize
```

Genera un archivo HTML con la visualizacion de las historias de conversacion. Se abre automaticamente en el navegador.

## Modo Interactivo de Aprendizaje

### 1. Entrenar interactivamente

```bash
rasa interactive
```

Modo interactivo que permite:
- Chatear con el bot
- Corregir predicciones incorrectas en tiempo real
- Anadir nuevas stories basadas en la conversacion
- Guardar los cambios automaticamente

## Inspeccion de Datos

### 1. Ver estadisticas de los datos de entrenamiento

```bash
rasa data split nlu
```

Divide los datos de NLU en training y test sets (80/20).

### 2. Ver configuracion del modelo entrenado

```bash
rasa show config
```

## Comandos de Depuracion

### 1. Ver logs detallados

```bash
rasa shell --debug
```

### 2. Exportar conversaciones

```bash
rasa export
```

Exporta las conversaciones almacenadas en el tracker store.

## Docker (si usas contenedores)

### Arquitectura de Modelos en Docker

**IMPORTANTE**: La imagen Docker de Rasa **NO incluye modelos pre-entrenados** en su interior. Los modelos se montan como volúmenes externos, siguiendo las mejores prácticas de separación entre código y datos.

**Ventajas de este enfoque**:
- ✅ Imagen Docker más liviana (~200-500MB menos)
- ✅ Actualizar modelos sin reconstruir la imagen
- ✅ Entrenar en una máquina, desplegar en otra
- ✅ Pipeline CI/CD más flexible
- ✅ Facilita A/B testing de modelos

### Flujo de Trabajo: Desarrollo → Producción

#### 1. Entrenar el modelo localmente

```bash
cd /home/hpoveda/Documents/AppChat/rasa

# Validar datos antes de entrenar
rasa data validate

# Entrenar modelo (genera nombre automático con timestamp)
rasa train

# O con nombre fijo si prefieres
rasa train --fixed-model-name transito_bot

# Verificar que el modelo se creó
ls -lh models/
```

El modelo entrenado se guarda en `./rasa/models/` con nombre aleatorio (ej: `20251112-172728-wary-kerf.tar.gz`) o con el nombre que especifiques.

**Nota**: El contenedor Docker detecta automáticamente cualquier archivo `.tar.gz` en el directorio de modelos, no necesitas un nombre específico.

#### 2. Transferir modelo a máquina de producción

Si entrenaste en una máquina diferente a donde vas a desplegar:

```bash
# Desde la máquina de entrenamiento (usa el nombre real del archivo)
scp ./rasa/models/20251112-172728-wary-kerf.tar.gz usuario@servidor:/ruta/al/proyecto/rasa/models/

# O usando git-lfs si el modelo no es muy grande
# O usando almacenamiento en la nube (S3, GCS, etc.)
```

**Importante**: El contenedor detecta automáticamente cualquier `.tar.gz`, no importa el nombre.

#### 3. Construir y ejecutar el contenedor

```bash
cd /home/hpoveda/Documents/AppChat

# Construir la imagen (solo contiene runtime, no el modelo)
docker-compose build rasa

# Iniciar el servicio (monta ./rasa/models como volumen)
docker-compose up -d rasa

# Verificar logs
docker-compose logs -f rasa
```

El contenedor:
- ✅ Detecta automáticamente cualquier modelo `.tar.gz` en `/app/models/`
- ✅ Si existe, lo carga y arranca el servidor
- ⚠️ Si NO existe, entrena un modelo como fallback (solo en desarrollo)
- ❌ Si no hay modelo ni datos, falla con un mensaje claro

#### 4. Actualizar modelo sin rebuild

Si entrenas una nueva versión del modelo:

```bash
# 1. Entrenar nuevo modelo localmente
cd /home/hpoveda/Documents/AppChat/rasa
rasa train

# 2. Opcional: eliminar modelos antiguos para ahorrar espacio
rm models/20251112-*.tar.gz  # (el nombre anterior)

# 3. Reiniciar solo el contenedor (sin rebuild)
cd /home/hpoveda/Documents/AppChat
docker-compose restart rasa

# El nuevo modelo se detecta y carga automáticamente
```

### Comandos Docker Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f rasa

# Verificar que el modelo está montado correctamente
docker-compose exec rasa ls -lh /app/models/

# Verificar salud del contenedor
docker-compose ps rasa

# Reiniciar servicio después de actualizar modelo
docker-compose restart rasa

# Reconstruir imagen (solo si cambias dependencias o configuración)
docker-compose build rasa
```

### Solución de Problemas Docker

#### Problema: "No pre-trained model found"

```bash
# Verificar que existe algún modelo .tar.gz en el host
ls -lh ./rasa/models/*.tar.gz

# Si no existe, entrenar el modelo
cd rasa
rasa train

# Reiniciar contenedor
cd ..
docker-compose restart rasa
```

#### Problema: Modelo desactualizado

```bash
# 1. Entrenar nuevo modelo
cd rasa
rasa train

# 2. Opcional: Limpiar modelos viejos
rm models/*-old-timestamp*.tar.gz

# 3. Reiniciar contenedor (NO rebuild)
cd ..
docker-compose restart rasa
```

#### Problema: Permisos de archivos

```bash
# El contenedor corre como usuario 'appuser' (UID 1000)
# Asegurar que los archivos tengan permisos correctos
sudo chown -R 1000:1000 ./rasa/models/
```

## Flujo de Trabajo Recomendado

### 1. Desarrollo inicial

```bash
# 1. Validar datos
rasa data validate

# 2. Entrenar modelo
rasa train

# 3. Probar en shell
rasa shell --debug

# 4. Evaluar modelo
rasa test nlu --cross-validation
```

### 2. Despues de modificar NLU (nlu.yml)

```bash
# 1. Validar
rasa data validate

# 2. Entrenar solo NLU
rasa train nlu

# 3. Probar clasificacion
rasa shell nlu

# 4. Probar conversacion completa
rasa shell
```

### 3. Despues de modificar Stories (stories.yml o rules.yml)

```bash
# 1. Validar
rasa data validate stories

# 2. Entrenar solo dialogo
rasa train core

# 3. Probar conversacion
rasa shell --debug

# 4. Visualizar historias
rasa visualize
```

## Estadisticas del Modelo Actual

- **Intents**: 107 intents definidos
- **Ejemplos de entrenamiento**: ~1,850 ejemplos
- **Rules**: 103 reglas
- **Stories**: 51 historias conversacionales
- **Responses**: 107 respuestas (utter_*)
- **Entities**: 2 (placa, cedula)

## Precision Esperada

Con el dataset actual enriquecido:
- **Intent Classification Accuracy**: >85%
- **Entity Extraction**: Depende del uso (placa, cedula)
- **Dialogue Policy Accuracy**: >90% (debido a rules bien definidas)

## Integracion con RAG (backRag)

El intent `consulta_codigo_transito` esta configurado para usar `action_default_fallback`, lo que permite integrarlo con el sistema RAG para consultas especificas al Codigo Nacional de Transito Terrestre.

Para activar la integracion:
1. Implementar un custom action que llame al servicio backRag
2. Modificar `domain.yml` para registrar el custom action
3. Iniciar el action server: `rasa run actions`

## Troubleshooting

### Problema: "No model found"
```bash
# Entrenar un nuevo modelo
rasa train
```

### Problema: "Could not load model"
```bash
# Verificar que el archivo de modelo existe
ls -la models/

# Re-entrenar si es necesario
rasa train
```

### Problema: Baja precision en intents
```bash
# Evaluar el modelo
rasa test nlu --cross-validation

# Ver matriz de confusion en results/
# Agregar mas ejemplos a los intents con baja precision en data/nlu.yml
```

### Problema: Bot no responde correctamente
```bash
# Probar en modo debug para ver que intent se detecta
rasa shell --debug

# Validar datos
rasa data validate

# Revisar rules.yml y stories.yml para el flujo correcto
```

## Recursos Adicionales

- Documentacion oficial de Rasa: https://rasa.com/docs/
- Rasa Community Forum: https://forum.rasa.com/
- Rasa YouTube Channel: https://www.youtube.com/c/RasaHQ

## Comandos Rapidos de Referencia

```bash
# ENTRENAMIENTO
rasa train                                  # Entrenar todo
rasa train nlu                              # Solo NLU
rasa train core                             # Solo dialogo

# PRUEBAS
rasa shell                                  # Modo interactivo
rasa shell --debug                          # Con informacion de debug
rasa shell nlu                              # Solo clasificacion de intents

# VALIDACION
rasa data validate                          # Validar todo
rasa data validate stories                  # Validar stories

# EVALUACION
rasa test nlu --cross-validation            # Evaluar modelo NLU
rasa visualize                              # Ver historias como grafo

# SERVIDORk
rasa run                                    # Iniciar servidor
rasa run --enable-api --cors "*"            # Con API habilitada
rasa run actions                            # Action server

# MODO INTERACTIVO
rasa interactive                            # Entrenar interactivamente
```

## Contacto y Contribuciones

Para reportar problemas o sugerir mejoras, contactar al equipo de desarrollo.


## flujo de historias
Saludo → inicio de interacción.

Planteamiento del problema → usuario describe o menciona su situación.

Consulta específica → solicita explicación sobre la infracción o norma.

Información del asistente → descripción legal, valor, tipo, consecuencias.

Guía práctica → cómo actuar, pagar, apelar o prevenir.

Cierre → agradecimiento, confirmación, despedida.