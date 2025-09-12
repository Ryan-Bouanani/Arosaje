FROM python:3.11-alpine as builder

WORKDIR /app

# Installation des dépendances de build
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.11-alpine

WORKDIR /app

# Copie des dépendances depuis le builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Installation des dépendances minimales
RUN apk add --no-cache curl postgresql-client

# Création des dossiers avec les bonnes permissions
RUN mkdir -p /app/assets/img /app/assets/temp_img /app/assets/persisted_img && \
    chmod -R 777 /app/assets

# Copie du code source
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Démarrer l'API directement (Neon PostgreSQL est toujours disponible)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --limit-concurrency 50"]
