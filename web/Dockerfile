# Image de base Node.js
FROM node:18-alpine

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances globales nécessaires
RUN npm install -g nuxt

# Copie des fichiers de configuration des dépendances
COPY package*.json ./

# Installation des dépendances du projet
RUN npm install

# Copie du reste des fichiers du projet
COPY . .

# Préparation de Nuxt
RUN npm run postinstall

# Exposition du port
EXPOSE 3000

# Configuration des variables d'environnement pour le développement
ENV HOST=0.0.0.0
ENV PORT=3000
ENV NODE_ENV=development
ENV NODE_OPTIONS='--no-warnings'

# Commande pour démarrer l'application en mode développement
CMD ["npm", "run", "dev"]