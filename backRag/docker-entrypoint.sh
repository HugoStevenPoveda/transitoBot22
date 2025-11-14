#!/bin/bash
set -e

echo "============================================"
echo "BackRag - Sistema RAG Initializing..."
echo "============================================"

# Check if ChromaDB is initialized
if [ ! -d "/app/data/chroma_db/chroma.sqlite3" ] && [ ! -f "/app/data/chroma_db/chroma.sqlite3" ]; then
    echo "⚠️  ChromaDB not initialized. Checking for setup requirements..."

    # Check if there are documents to process
    if [ -d "/app/data/documents" ] && [ "$(ls -A /app/data/documents)" ]; then
        echo "📄 Documents found. Running database setup..."
        python scripts/setup_database.py
        echo "✅ Database setup completed"
    else
        echo "⚠️  No documents found in /app/data/documents"
        echo "⚠️  ChromaDB will be initialized empty"
        echo "⚠️  You can add documents and restart the container"
    fi
else
    echo "✅ ChromaDB already initialized"
fi

echo "============================================"
echo "🚀 Starting BackRag API Server on port 8000"
echo "============================================"

# Execute the main command
exec "$@"
