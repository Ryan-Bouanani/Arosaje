#!/bin/bash

# Script pour exécuter les tests de l'API localement
# Usage: ./run_tests.sh [nom_du_fichier_test]

# Variables d'environnement pour les tests
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/arosaje_test"
export REDIS_URL="redis://localhost:6379"
export ENVIRONMENT="test"
export JWT_SECRET="test_secret_key_local"

# Vérifier si l'API est déjà en cours d'exécution
if curl -s http://localhost:8000/health > /dev/null; then
    echo "🔍 API déjà en cours d'exécution"
else
    echo "🚀 Démarrage de l'API pour les tests..."
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
    API_PID=$!
    echo "⏳ Attente du démarrage de l'API..."
    sleep 5
fi

# Installer les dépendances de test si nécessaire
if ! pip list | grep -q "tavern"; then
    echo "📦 Installation des dépendances de test..."
    pip install -r requirements-test.txt
fi

# Création des dossiers nécessaires
mkdir -p assets/persisted_img
mkdir -p assets/temp_img
mkdir -p assets/img
mkdir -p logs

# Si un nom de fichier de test spécifique est fourni, exécuter ce test
# Sinon, exécuter tous les tests
if [ -n "$1" ]; then
    echo "🧪 Exécution du test: $1"
    pytest "$1" -v
else
    echo "🧪 Exécution de tous les tests..."
    pytest tests/workflows/ -v
fi

# Si nous avons démarré l'API, l'arrêter
if [ -n "$API_PID" ]; then
    echo "🛑 Arrêt de l'API..."
    kill $API_PID
fi

echo "✅ Tests terminés" 