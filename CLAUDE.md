# 🌿 A'rosa-je - Documentation Complète du Projet

## 📋 Vue d'ensemble
Application mobile de garde de plantes permettant aux propriétaires de faire garder leurs plantes et aux botanistes de fournir des conseils professionnels.

## 🏗️ Architecture Technique

### Stack Technique
- **Mobile**: Flutter/Dart avec Provider pour la gestion d'état
- **Backend**: FastAPI (Python) avec SQLAlchemy ORM
- **Base de données**: PostgreSQL
- **Cache/Sessions**: Redis
- **Containerisation**: Docker & Docker Compose
- **Monitoring**: Grafana + Prometheus + InfluxDB

### Structure du Projet
```
EPSI-MSPR6.1/
├── api/                    # Backend FastAPI
│   ├── models/            # Modèles SQLAlchemy
│   ├── schemas/           # Schémas Pydantic
│   ├── crud/              # Opérations CRUD
│   ├── routers/           # Endpoints API
│   ├── services/          # Services métier
│   └── utils/             # Utilitaires
├── mobile/                # Application Flutter
│   └── lib/
│       ├── models/        # Modèles Dart
│       ├── services/      # Services API
│       ├── providers/     # State management
│       └── views/         # Écrans UI
├── bin/                   # Scripts utilitaires
└── docker-compose.yml     # Orchestration
```

## 🔑 Systèmes Fonctionnels

### 1. Système d'Authentification
- **JWT** avec refresh tokens
- **Rôles**: USER, BOTANIST, ADMIN
- Vérification email requise pour nouveaux comptes (sauf comptes de test)

### 2. Système de Garde de Plantes (PlantCare)
- Création de demandes de garde avec dates et instructions
- Statuts: PENDING, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED
- Géolocalisation des gardes
- Assignation gardien/propriétaire

### 3. Système de Rapports de Garde (CareReport)
- Rapports créés par les gardiens pendant la garde
- Photos avant/après avec descriptions
- Historique complet des actions
- Accessible uniquement pendant la période de garde active

### 4. Système de Conseils Botaniques (PlantCareAdvice)
- **Deux onglets principaux**:
  - **"À examiner"**: Gardes sans aucun avis de botaniste
  - **"Avis"**: Gardes ayant reçu au moins un avis (de n'importe quel botaniste)
- **Versioning des conseils**: Chaque modification crée une nouvelle version
- **Validation croisée**: Les botanistes peuvent valider les conseils d'autres botanistes
- **Priorités**: NORMAL, URGENT, FOLLOW_UP
- **Statuts de validation**: PENDING, VALIDATED, REJECTED

### 5. Système de Messagerie
- WebSocket pour temps réel
- Conversations entre utilisateurs
- Notifications push
- Historique persistant

### 6. Système Admin
- **Backend fonctionnel**:
  - `/admin/pending-verifications`: Liste des comptes en attente
  - `/admin/verify/{user_id}`: Valider un compte
  - `/admin/reject/{user_id}`: Rejeter un compte
- **Frontend à implémenter** (vision proposée):
  - Dashboard avec statistiques
  - Gestion des validations de comptes
  - Gestion des utilisateurs
  - Monitoring système

## 👤 Comptes de Test

### Utilisateurs de base
```
# Admin
Email: root@arosaje.fr
Password: epsi691
Rôle: ADMIN

# Utilisateur standard
Email: user@arosaje.fr
Password: epsi691
Rôle: USER

# Botaniste
Email: botanist@arosaje.fr
Password: epsi691
Rôle: BOTANIST
```

## 🚀 Commandes de Développement

### Démarrage rapide
```bash
# Configuration initiale (première fois seulement)
./bin/setup-env          # Configure les variables d'environnement
./bin/setup-api          # Configure l'environnement Python

# Lancement des services
./bin/up all             # Démarre tous les services
./bin/up api             # Démarre seulement l'API
./bin/up mobile          # Démarre seulement le mobile

# Arrêt propre
CTRL+C                   # Arrête tous les conteneurs
```

### URLs des Services
- **API**: http://localhost:8000 (Swagger: /docs)
- **Mobile Web**: http://localhost:5000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### Debug et Logs
```bash
# Voir les logs d'un service
docker logs arosa-je-api -f
docker logs arosa-je-mobile -f

# Se connecter à un conteneur
docker exec -it arosa-je-api bash
docker exec -it arosa-je-mobile sh

# Voir les conteneurs actifs
docker ps
```

## 🔍 Points d'Attention Importants

### Logique des Boutons (PlantCareDetails)
1. **"Faire un rapport"**: 
   - Visible uniquement pour le gardien assigné
   - Grisé si la garde n'a pas encore commencé
   - Actif pendant la période de garde

2. **Conseils Botaniques (PlantCareAdviceCard)**:
   - **"Modifier l'avis"** (orange): Si c'est mon propre avis
   - **"Valider"** (bleu): Si c'est l'avis d'un autre botaniste et non validé
   - Pas de bouton si l'avis est déjà validé

### Filtrage Global des Gardes (Botanistes)
- Une garde avec un avis de **n'importe quel botaniste** passe de "À examiner" à "Avis"
- Cela permet la collaboration entre botanistes
- Un botaniste peut toujours ajouter son avis même si d'autres botanistes en ont déjà donné

### Statistiques du Profil Botaniste
Affiche 3 métriques personnelles:
1. **Mes Conseils**: Nombre total de conseils donnés
2. **Validés**: Mes conseils validés par d'autres botanistes
3. **Validations Faites**: Nombre de conseils d'autres botanistes que j'ai validés

## 🐛 Problèmes Connus et Solutions

### Service Worker Cache (Flutter Web)
- Problème: Cache agressif empêchant les mises à jour
- Solution: Vider le cache navigateur ou mode incognito pour tests

### Docker sur Windows
- Assurez-vous que Docker Desktop est lancé
- Utilisez PowerShell ou Git Bash, pas CMD
- Les scripts bin/ peuvent nécessiter chmod +x

### Migrations Alembic
```bash
# Créer une nouvelle migration
docker exec -it arosa-je-api bash
cd /app
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 📝 Conventions de Code

### Flutter/Dart
- Utiliser Provider pour la gestion d'état
- Services singleton avec pattern `await ServiceName.init()`
- Gestion des erreurs avec try-catch et messages utilisateur
- Vérification `mounted` avant setState/Navigator

### FastAPI/Python
- CRUD pattern pour les opérations base de données
- Schemas Pydantic pour validation
- Dependency injection avec Depends()
- Gestion des erreurs avec HTTPException

## 🔄 Workflow Git
- Branch `main` pour la production
- Commits atomiques avec messages descriptifs
- Pull avant push pour éviter les conflits

## 📚 Documentation Additionnelle
- `/docs/database_uml.md`: Modèle de données complet
- `/docs/architecture_schema.md`: Schémas d'architecture
- `/docs/postgresql_justification.md`: Choix techniques
- API Swagger: http://localhost:8000/docs

## ⚠️ Important - Instructions de Développement
- **Do what has been asked; nothing more, nothing less**
- **NEVER create files unless they're absolutely necessary for achieving your goal**
- **ALWAYS prefer editing an existing file to creating a new one**
- **NEVER proactively create documentation files (*.md) or README files unless explicitly requested**
- Ne jamais commiter les fichiers `.env`
- Toujours tester les changements sur les 3 rôles (USER, BOTANIST, ADMIN)
- Vérifier la compatibilité mobile web avant de pousser
- Les middlewares de monitoring sont critiques, ne pas les désactiver en production

---
*Dernière mise à jour: 30/08/2025*