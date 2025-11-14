# ============================================
# Stage 1: Build and install dependencies
# ============================================
FROM python:3.11-slim-bookworm AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
# gcc, g++ needed for some Python packages like numpy, torch
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv using pip (more reliable in Docker)
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install Python dependencies using uv
# This includes FastAPI, ChromaDB, Sentence Transformers, PyTorch, Anthropic
RUN uv pip install --system --no-cache -r requirements.txt

# Pre-download the sentence-transformers model to avoid downloading at runtime
# This significantly reduces startup time
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# ============================================
# Stage 2: Runtime environment
# ============================================
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install only runtime dependencies (no build tools needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy pre-downloaded sentence-transformers models
COPY --from=builder /root/.cache /home/appuser/.cache

# Create necessary directories for ChromaDB and data
RUN mkdir -p /app/data/chroma_db /app/data/cache /app/data/documents && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./scripts ./scripts
COPY --chown=appuser:appuser ./pyproject.toml ./run.py ./
COPY --chown=appuser:appuser ./docker-entrypoint.sh /docker-entrypoint.sh

# Copy data directory structure (documents may be mounted as volume)
COPY --chown=appuser:appuser ./data/documents ./data/documents

# Make entrypoint executable
USER root
RUN chmod +x /docker-entrypoint.sh
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    CHROMA_DB_PATH=/app/data/chroma_db \
    EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health').read()" || exit 1

# Use entrypoint script for initialization
ENTRYPOINT ["/docker-entrypoint.sh"]

# Run the application
CMD ["python", "run.py"]
