FROM python:3.11-alpine as builder

WORKDIR /app

# Installation des dépendances de build
RUN apk add --no-cache gcc musl-dev libffi-dev

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
RUN apk add --no-cache sqlite curl

# Création des dossiers avec les bonnes permissions
RUN mkdir -p /app/assets/database /app/assets/img && \
    chmod -R 777 /app/assets

# Copie du code source
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Optimisation des workers Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000",  "--workers", "2", "--limit-concurrency", "50"]
