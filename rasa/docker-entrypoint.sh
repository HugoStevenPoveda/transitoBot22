#!/bin/bash
set -e

echo "============================================"
echo "RASA - Conversational AI System"
echo "============================================"

# Check if any model exists in /app/models/
MODEL_FILE=$(find /app/models -name "*.tar.gz" -type f | head -n 1)

if [ -n "$MODEL_FILE" ]; then
    MODEL_NAME=$(basename "$MODEL_FILE")
    MODEL_SIZE=$(du -h "$MODEL_FILE" | cut -f1)
    echo "✅ Pre-trained model found: $MODEL_NAME"
    echo "   Model size: ${MODEL_SIZE}"
    echo "   Model path: $MODEL_FILE"

    # Update RASA_MODEL_PATH to point to the detected model
    export RASA_MODEL_PATH="$MODEL_FILE"
else
    echo "⚠️  No pre-trained model found in /app/models/"
    echo "   Checking for training data..."

    if [ -d "/app/data" ] && [ "$(ls -A /app/data)" ]; then
        echo "📚 Training data found. Training model now..."
        rasa train --fixed-model-name transito_bot

        if [ -f "/app/models/transito_bot.tar.gz" ]; then
            echo "✅ Model trained successfully!"
            export RASA_MODEL_PATH="/app/models/transito_bot.tar.gz"
        else
            echo "❌ Model training failed!"
            exit 1
        fi
    else
        echo "❌ No training data found!"
        echo "   Cannot start RASA without a model."
        exit 1
    fi
fi

# Update endpoints.yml with Docker environment
if [ -f "/app/endpoints.yml" ]; then
    echo "📝 Configuring action server endpoint..."
    sed -i 's|http://localhost:5055|http://localhost:5055|g' /app/endpoints.yml
fi

echo "============================================"
echo "🚀 Starting RASA Services"
echo "   - RASA Server: port 5005"
echo "   - Actions Server: port 5055"
echo "============================================"

# Execute the main command
exec "$@"
