#!/bin/bash

# Script d'installation Flutter pour Netlify

set -e

echo "🚀 Installing Flutter for Netlify..."

# Créer le dossier Flutter
mkdir -p /opt/flutter

# Télécharger Flutter
cd /opt/flutter
wget -q https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.3-stable.tar.xz
tar xf flutter_linux_3.24.3-stable.tar.xz

# Ajouter Flutter au PATH
export PATH="$PATH:/opt/flutter/flutter/bin"

# Vérifier l'installation
flutter --version

# Accepter les licences Android (nécessaire pour Flutter web)
flutter doctor --android-licenses || true

# Activer Flutter web
flutter config --enable-web

echo "✅ Flutter installed successfully!"