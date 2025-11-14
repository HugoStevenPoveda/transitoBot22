# ============================================
# Stage 1: Build and install dependencies
# ============================================
FROM python:3.11-slim-bookworm AS builder

# Set working directory
WORKDIR /app

# Install uv using pip (more reliable in Docker)
# https://github.com/astral-sh/uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install Python dependencies using uv
# uv is much faster than pip for dependency resolution
RUN uv pip install --system --no-cache -r requirements.txt

# ============================================
# Stage 2: Runtime environment
# ============================================
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./pyproject.toml ./

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()" || exit 1

# Run the application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
