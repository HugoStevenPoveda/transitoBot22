# Modelos RASA

Esta carpeta contiene los modelos pre-entrenados de RASA.

## Modelo actual

- **Archivo**: `20251119-154152-denim-dove.tar.gz`
- **Tamaño**: ~37 MB
- **Fecha**: 19 de Noviembre 2024

## Obtener el modelo

El modelo no está incluido en el repositorio Git debido a su tamaño.

**Opción 1: Descargar desde servidor/drive**
```bash
# URL de descarga (configurar según disponibilidad)
wget [URL_DEL_MODELO] -O ./models/20251119-154152-denim-dove.tar.gz
```

**Opción 2: Copiar desde instalación local**
```bash
# Si tienes el modelo en otra instalación
cp /path/to/rasa/models/20251119-154152-denim-dove.tar.gz ./models/
```

**Opción 3: Entrenar un nuevo modelo**
```bash
# Desde el directorio rasa del proyecto
cd ../rasa
rasa train
# Copiar el modelo generado
cp models/[MODELO_GENERADO].tar.gz ../transibot/models/
# Actualizar RASA_MODEL_PATH en docker-compose.yml
```

## Configuración

Asegúrate de que `docker-compose.yml` tenga el path correcto:

```yaml
environment:
  - RASA_MODEL_PATH=/app/models/20251119-154152-denim-dove.tar.gz
```
