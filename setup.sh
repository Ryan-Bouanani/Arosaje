#!/bin/bash

echo "🔧 Initialisation des conteneurs Docker..."

# Vérifier que Docker et Docker Compose sont installés
if ! [ -x "$(command -v docker)" ]; then
  echo "❌ Docker n'est pas installé. Veuillez l'installer."
  exit 1
fi

if ! [ -x "$(command -v docker-compose)" ]; then
  echo "❌ Docker Compose n'est pas installé. Veuillez l'installer."
  exit 1
fi

# Construire les conteneurs
echo "🚀 Construction des conteneurs..."
docker-compose build

# Lancer les conteneurs et attacher les logs au terminal
echo "▶️ Lancement des conteneurs et attachement des logs..."
echo "🌐 Documentation API: http://127.0.0.1:8000/docs"
docker-compose up
