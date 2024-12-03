# Utiliser l'image officielle Node.js
FROM node:18-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers package.json et package-lock.json
COPY package*.json ./

# Installer les dépendances
RUN npm install -g npm@latest
RUN npm install

# Copier le reste des fichiers du projet
COPY . .

# Exposer le port utilisé par Nuxt
EXPOSE 3000

# Commande pour démarrer l'application
CMD ["npm", "run", "dev"]
