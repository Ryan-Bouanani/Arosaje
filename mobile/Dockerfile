FROM instrumentisto/flutter:latest

WORKDIR /app

ENV FLUTTER_SUPPRESS_ANALYTICS=true
ENV CI=true

# Copier d'abord les fichiers de dépendances (changent rarement)
COPY pubspec.yaml pubspec.lock ./

# Installer les dépendances (cette couche sera mise en cache)
RUN flutter pub get

# Copier le code source ensuite (change souvent)
COPY . .

# Builder l'application
RUN flutter build web

# Installer nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copier les fichiers web buildés
RUN cp -r build/web/* /var/www/html/

# Configuration nginx
RUN sed -i 's/listen 80/listen 5000/g' /etc/nginx/sites-enabled/default

EXPOSE 5000

CMD ["nginx", "-g", "daemon off;"]