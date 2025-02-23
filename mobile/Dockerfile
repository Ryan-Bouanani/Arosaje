FROM instrumentisto/flutter:latest


WORKDIR /app

# Copie des fichiers du projet
COPY . .

# Obtenir les dépendances
RUN flutter pub get

# Build l'application (pour le web dans ce cas, car dans un conteneur)
RUN flutter build web

# Installer et utiliser un serveur web léger pour servir l'application
RUN apt-get update && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers buildés dans le dossier nginx
RUN cp -r build/web/* /var/www/html/

EXPOSE 80   

CMD ["nginx", "-g", "daemon off;"] 