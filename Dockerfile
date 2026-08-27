FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Instalar dependencias esenciales de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    -r requirements/base.txt \
    -r requirements/api.txt \
    -r requirements/updater.txt

# Copiar código fuente y herramientas
COPY src/ /app/src/
COPY deploy/ /app/deploy/
COPY scripts/ /app/scripts/
COPY env.example.py /app/env.example.py

# Directorios de datos y logs
RUN mkdir -p /app/data/staging /app/logs && \
    chmod +x /app/scripts/*.sh || true

ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080"]
