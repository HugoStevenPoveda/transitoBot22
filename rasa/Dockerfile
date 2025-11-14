# ============================================
# Stage 1: Build, install dependencies and train model
# ============================================
FROM python:3.10-slim-bookworm AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
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
COPY pyproject.toml ./
COPY uv.lock* ./

# Install RASA and dependencies using uv
# RASA requires Python 3.10 specifically for best compatibility
# Use --system to install directly to system Python instead of creating venv
RUN uv pip install --system -r pyproject.toml

# Copy RASA configuration and training data
COPY config.yml domain.yml endpoints.yml credentials.yml ./
COPY data/ ./data/
COPY actions/ ./actions/

# ============================================
# Stage 2: Runtime environment
# ============================================
FROM python:3.10-slim-bookworm

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy RASA configuration files
COPY --chown=appuser:appuser config.yml domain.yml credentials.yml ./
COPY --chown=appuser:appuser endpoints.yml ./endpoints.yml
COPY --chown=appuser:appuser data/ ./data/
COPY --chown=appuser:appuser actions/ ./actions/

# Copy startup scripts
COPY --chown=appuser:appuser docker-entrypoint.sh /docker-entrypoint.sh
COPY --chown=appuser:appuser start-rasa.sh /start-rasa.sh

# Make scripts executable
RUN chmod +x /docker-entrypoint.sh /start-rasa.sh

# Create empty directory for models (mounted from volume)
# Models are trained externally and mounted via docker-compose volume
RUN mkdir -p /app/models && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    RASA_MODEL_PATH=/app/models/transito_bot.tar.gz

# Expose ports
# 5005: RASA server
# 5055: RASA actions server
EXPOSE 5005 5055

# Health check for RASA server
# RASA takes ~60s to load model, so we give it plenty of time
HEALTHCHECK --interval=15s --timeout=10s --start-period=120s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5005/').read()" || exit 1

# Use entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]

# Start RASA with both server and actions
CMD ["/start-rasa.sh"]
