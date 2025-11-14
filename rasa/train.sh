#!/bin/bash
# Script para entrenar el modelo RASA

echo "🚀 Iniciando entrenamiento de RASA..."
echo "📁 Directorio: $(pwd)"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "domain.yml" ]; then
    echo "❌ Error: No se encuentra domain.yml"
    echo "   Por favor ejecuta este script desde el directorio rasa/"
    exit 1
fi

# Buscar instalación de RASA
if command -v rasa &> /dev/null; then
    echo "✓ RASA encontrado en PATH global"
    RASA_CMD="rasa"
elif [ -f ".venv/bin/rasa" ]; then
    echo "✓ RASA encontrado en .venv/bin/rasa"
    RASA_CMD=".venv/bin/rasa"
elif command -v python -m rasa &> /dev/null; then
    echo "✓ RASA disponible como módulo Python"
    RASA_CMD="python -m rasa"
else
    echo "❌ Error: RASA no está instalado"
    echo ""
    echo "Para instalar RASA, ejecuta:"
    echo "  pip install rasa"
    echo ""
    exit 1
fi

echo ""
echo "🏋️  Entrenando modelo con configuración actualizada..."
echo "   - FallbackClassifier activado"
echo "   - Nuevos intents: out_of_scope, consulta_codigo_transito"
echo "   - Reglas de fallback configuradas"
echo ""

# Entrenar modelo
$RASA_CMD train --fixed-model-name transito_bot_v2

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ ¡Entrenamiento completado exitosamente!"
    echo ""
    echo "Modelo guardado en: models/transito_bot_v2.tar.gz"
    echo ""
    echo "Para probar el modelo:"
    echo "  $RASA_CMD shell"
    echo ""
    echo "Para ejecutar el servidor:"
    echo "  $RASA_CMD run --enable-api --cors \"*\""
    echo ""
    echo "Para ejecutar el servidor de actions:"
    echo "  $RASA_CMD run actions"
    echo ""
else
    echo ""
    echo "❌ Error durante el entrenamiento (código: $EXIT_CODE)"
    echo ""
    exit $EXIT_CODE
fi
