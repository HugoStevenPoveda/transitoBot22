#!/bin/bash
set -e

# Function to handle shutdown gracefully
shutdown() {
    echo ""
    echo "🛑 Shutting down RASA services..."

    if [ ! -z "$ACTIONS_PID" ]; then
        echo "   Stopping actions server (PID: $ACTIONS_PID)..."
        kill -TERM "$ACTIONS_PID" 2>/dev/null || true
    fi

    if [ ! -z "$RASA_PID" ]; then
        echo "   Stopping RASA server (PID: $RASA_PID)..."
        kill -TERM "$RASA_PID" 2>/dev/null || true
    fi

    wait
    echo "✅ All services stopped"
    exit 0
}

# Trap SIGTERM and SIGINT signals
trap shutdown SIGTERM SIGINT

echo ""
echo "🚀 Starting RASA Actions Server on port 5055..."
rasa run actions --port 5055 &
ACTIONS_PID=$!
echo "   Actions Server PID: $ACTIONS_PID"

# Wait a bit for actions server to start
sleep 3

echo ""
echo "🚀 Starting RASA Server on port 5005..."
echo "   Model: ${RASA_MODEL_PATH:-/app/models/transito_bot.tar.gz}"
echo "   CORS: Enabled (*)"
echo "   API: Enabled"
echo ""

rasa run \
    --enable-api \
    --cors "*" \
    --port 5005 \
    --endpoints endpoints.yml \
    --credentials credentials.yml &
RASA_PID=$!
echo "   RASA Server PID: $RASA_PID"

echo ""
echo "============================================"
echo "✅ RASA Services Running"
echo "   RASA Server: http://localhost:5005"
echo "   Actions Server: http://localhost:5055"
echo "   API Docs: http://localhost:5005/docs"
echo "============================================"
echo ""

# Wait for both processes
wait $RASA_PID $ACTIONS_PID

# If we reach here, one of the processes died
echo "❌ One of the services stopped unexpectedly"
exit 1
