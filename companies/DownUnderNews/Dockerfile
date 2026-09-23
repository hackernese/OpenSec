# =============================================================================
# The Down Under News – Backend Dockerfile
# =============================================================================

FROM python:3.12-slim

# Prevent .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed by psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (backup/ excluded via .dockerignore)
COPY . .

# Create non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app
USER appuser

EXPOSE 5000

# Wait-for-DB + run migrations + start Gunicorn
CMD ["sh", "-c", "\
    echo 'Waiting for database...' && \
    until python -c \"import psycopg2; psycopg2.connect( \
        host='${DB_HOST:-db}', \
        port='${DB_PORT:-5432}', \
        dbname='${DB_NAME:-newspaper_db}', \
        user='${DB_USER:-news_user}', \
        password='${DB_PASSWORD:-news_pass}' \
    )\" 2>/dev/null; do sleep 1; done && \
    echo 'Database ready.' && \
    flask db upgrade 2>/dev/null || true && \
    gunicorn wsgi:app \
        --bind 0.0.0.0:5000 \
        --workers 4 \
        --worker-class gthread \
        --threads 2 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
    "]
