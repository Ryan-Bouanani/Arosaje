# 🌿 A'rosa-je - Gestion de Plantes

**Projet réalisé dans le cadre de la MSPR 6.1 - EPSI**  
**Titre professionnel : Concepteur Développeur d’Applications (CDA)**  
**RNCP 31678**

---

## 📖 Description du Projet

A'rosa-je est une application mobile et web destinée à aider les particuliers à mieux s’occuper de leurs plantes. Ce projet vise à répondre aux besoins croissants des utilisateurs en proposant un système de partage de photos et de conseils entre propriétaires et botanistes. 

L’application inclut : 
- Une interface mobile pour photographier les plantes, consulter les conseils, et organiser leur garde.
- Une interface web pour la gestion des données utilisateurs, le stockage des informations et la communication avec une base de données centralisée.

---

## 🛠️ Fonctionnalités Clés

1. **Gestion des plantes**  
   - Affichage des plantes à faire garder.  
   - Prise et partage de photos avant et après entretien.  

2. **Conseils d’entretien**  
   - Ajout et visualisation de recommandations par les botanistes.  

3. **Système de conseils botaniques**  
   - Interface dédiée aux botanistes pour examiner les gardes et donner des avis.
   - Validation croisée : les botanistes peuvent valider les conseils d'autres collègues.
   - Priorisation des conseils (NORMAL, URGENT, FOLLOW_UP).
   - Versioning des conseils avec historique des modifications.

4. **Communication temps réel**  
   - Messagerie intégrée avec WebSocket pour les discussions instantanées.
   - Coordination entre propriétaires, gardiens et botanistes.  

5. **Historique utilisateur**  
   - Suivi des plantes gardées ou en garde via des profils détaillés.
   - Rapports de garde avec photos avant/après entretien.  

---

## 🧰 Technologies Utilisées

### **Mobile : Flutter**  
- Développement rapide grâce à un codebase unique pour Android et iOS.  
- Interface utilisateur riche basée sur des widgets personnalisables.  
- Excellente gestion des animations pour une expérience fluide.  

### **Frontend Web : Vue.js (Nuxt.js & Vuetify)**  
- Création d’un frontend modulaire et réactif.  
- Vuetify pour un design moderne et une intégration rapide des composants UI.  
- Nuxt.js pour la gestion des routes et la génération côté serveur (SSR).  

### **Backend : FastAPI (Python)**  
- API REST rapide et évolutive avec gestion des opérations asynchrones.  
- Intégration facile avec l’ORM SQLAlchemy pour la gestion des données.  

### **Base de Données : PostgreSQL avec SQLAlchemy**  
- Migration de SQLite vers PostgreSQL pour de meilleures performances et fonctionnalités avancées.  
- Support JSON/JSONB natif, full-text search, et gestion de la concurrence optimisée.  
- SQLAlchemy ORM pour une abstraction robuste des données.

### **Cache et Session : Redis**  
- Cache haute performance pour améliorer les temps de réponse.  
- Gestion des sessions utilisateur et rate limiting.  
- Support WebSocket pour la messagerie temps réel.
- Interface d'administration via RedisInsight (http://localhost:8001).

### **Monitoring : Stack Observabilité**  
- **Grafana** : Dashboards et visualisation des métriques.  
- **Prometheus** : Collecte et stockage des métriques système et applicatives.  
- **InfluxDB** : Base de données time-series pour les données analytiques.

### **Containerisation : Docker & Docker Compose**  
- Uniformisation des environnements de développement.  
- Orchestration complète de tous les services (API, Web, Mobile, BDD, Monitoring).  

---

## 📋 Cahier des Charges et Livrables

### **Cahier des Charges**
- Développement d’une application mobile et web répondant aux besoins exprimés.  
- Mise en œuvre d’une architecture organisée en couches (MVC).  
- Respect des bonnes pratiques de développement logiciel.

### **Livrables**
1. Application fonctionnelle (mobile et web).  
2. Documentation technique complète :  
   - **UML Base de données** (`docs/database_uml.md`) : Modèle complet des entités et relations.  
   - **Architecture applicative** (`docs/architecture_schema.md`) : Schémas détaillés de l'infrastructure.  
   - **Justifications techniques** :
     - PostgreSQL vs SQLite (`docs/postgresql_justification.md`)  
     - REST vs GraphQL (`docs/graphql_vs_rest_benchmark.md`)  
   - Maquettes des interfaces et plans de tests fonctionnels.  
3. Fichiers de containerisation et orchestration Docker Compose.  
4. Stack de monitoring et observabilité intégrée.

---

## 🧪 Tests Réalisés

Une suite complète de tests a été implémentée couvrant tous les aspects de l'application :

### **Tests Unitaires** (38 tests - 100% de réussite)
- **Sécurité** : Tests des utilitaires JWT, hachage des mots de passe, validation des tokens
- **Modèles** : Tests des entités de base de données (PlantCare, User, etc.)
- **CRUD** : Tests des opérations de création, lecture, mise à jour et suppression

### **Tests d'Intégration**
- **Base de données** : Tests de connexion, contraintes, transactions
- **API** : Tests des endpoints avec authentification et autorisation
- **Services** : Tests des interactions entre composants

### **Tests de Workflows (Tavern)**
- **Authentification complète** : Inscription, connexion, refresh token
- **Gestion des plantes** : CRUD complet avec gestion des permissions
- **Conseils botaniques** : Workflow de validation croisée

### **Exécution des Tests**
```bash
# Lancer tous les tests
docker exec arosa-je-api python run_tests.py

# Tests unitaires uniquement
docker exec arosa-je-api python -m pytest tests/unit/ -v

# Tests d'intégration uniquement  
docker exec arosa-je-api python -m pytest tests/integration/ -v

# Tests de workflows uniquement
docker exec arosa-je-api python -m pytest tests/workflows/ -v
```  

---

## 📦 Installation et Déploiement

### **Prérequis**
- Docker & Docker Compose
- Git
- Python 3.11+ (pour l'API)

### **Étapes d'installation**
```bash
# Cloner le dépôt
git clone <repository-url>

# Rendre les scripts exécutables
chmod +x bin/up bin/update bin/setup-api bin/setup-env


# Configurer les variables d'environnement
bin/setup-secrets

# Configurer les variables d'environnement
bin/setup-env

# Configurer l'environnement Python pour l'API
bin/setup-api

# Démarrer tous les services
bin/up all

# Mettre à jour tous les dépôts
bin/update
```

### **⚠️ Important**
Avant de lancer `bin/up`, assurez-vous d'avoir :
1. Configuré les variables d'environnement avec `bin/setup-env`
2. Initialisé l'API avec `bin/setup-api`

Sans ces étapes préalables, l'application ne fonctionnera pas correctement.

### **🌐 Services & URLs**

#### Production 🚀
| Service | Description | URL Production | Technologies |
|---------|------------|----------------|--------------|
| **API** | Backend API | https://arosaje-backend-t2x7.onrender.com | FastAPI (Python) + Render |
| **Mobile** | App Flutter (Web) | https://ryan-bouanani.github.io/Arosaje/ | Flutter + GitHub Pages |
| **Base de données** | Base de données | Neon PostgreSQL (cloud) | PostgreSQL 17 |

#### Développement Local 🏠
| Service | Description | URL Locale | Technologies |
|---------|------------|------------|--------------|
| **API** | Backend API | http://localhost:8000 | FastAPI (Python) |
| **Web** | Interface Web | http://localhost:3000 | Vue.js (Nuxt.js) |
| **Mobile** | App Flutter (Web) | http://localhost:5000 | Flutter |
| **PostgreSQL** | Base de données | localhost:5432 | PostgreSQL 15 |
| **Redis** | Cache & Sessions | localhost:6379 | Redis 7 |
| **RedisInsight** | Interface Redis | http://localhost:8001 | RedisInsight |
| **Grafana** | Monitoring Dashboard | http://localhost:3001 | Grafana |
| **Prometheus** | Métriques | http://localhost:9090 | Prometheus |
| **InfluxDB** | Time Series DB | localhost:8086 | InfluxDB |

### **🛠️ Scripts Utilitaires**

| Script | Description | Utilisation |
|--------|------------|-------------|
| `bin/up` | Gestion des conteneurs | `bin/up all` pour démarrer la stack |
| `bin/update` | Mise à jour des dépôts | `bin/update` pour synchroniser avec main |
| `bin/setup-api` | Configuration de l'API | `bin/setup-api` pour gérer les dépendances Python |

#### Commandes Spéciales
- `CTRL+C` : Arrêter proprement tous les conteneurs

### **📝 Documentation API & Monitoring**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Grafana Dashboards**: http://localhost:3001 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Documentation Technique**: Dossier `docs/` avec UML, architecture et justifications

### **👤 Comptes de Test**

Pour tester l'application, utilisez ces comptes préconfigurés :

```
Admin
Email: root@arosaje.fr
Password: epsi691
Rôle: ADMIN (gestion complète)

Utilisateur standard
Email: user@arosaje.fr  
Password: epsi691
Rôle: USER (propriétaire de plantes)

Botaniste
Email: botanist@arosaje.fr
Password: epsi691
Rôle: BOTANIST (conseils et validation)
```

**Note** : Ces comptes sont automatiquement créés au premier démarrage de l'application.

### **🏭 Système de Données de Test (Factory_boy + Faker)**

A'rosa-je utilise un système professionnel de génération de données basé sur **factory_boy** et **Faker** pour créer des données françaises réalistes :

#### **Génération de Données Professionnelle**
```bash
# Scénarios prédéfinis
docker exec arosa-je-api python seeders/run.py demo     # 20 users + 8 plantes (recommandé pour démo)
docker exec arosa-je-api python seeders/run.py dev      # 100+ entités pour développement
docker exec arosa-je-api python seeders/run.py test     # 500+ entités pour tests de performance
docker exec arosa-je-api python seeders/run.py minimal  # Configuration minimale

# Chargement personnalisé
docker exec arosa-je-api python seeders/run.py load --users 50 --botanists 10 --plants 30

# Gestion et monitoring
docker exec arosa-je-api python seeders/run.py status          # Statistiques de la base
docker exec arosa-je-api python seeders/run.py reset --confirm # Reset complet sécurisé
docker exec arosa-je-api python test_factories.py             # Test dry-run sans DB
```

#### **Données Françaises Réalistes**
- **Noms et prénoms** : Générés avec Faker français (fr_FR)
- **Villes** : Principales villes françaises (Paris, Lyon, Marseille, etc.)
- **Téléphones** : Format français correct (ex: 06.12.34.56.78)
- **Emails** : Domaines français réalistes (@gmail.fr, @orange.fr, @jardin-[ville].fr pour botanistes)
- **Plantes** : 8 vraies espèces avec images et descriptions botaniques professionnelles

#### **Architecture Modulaire**
- **UserFactory** : Utilisateurs français avec répartition 85% USER / 15% BOTANIST
- **PlantFactory** : 8 espèces réelles avec mapping vers vraies images
- **Factories avancées** : PlantCare, Advice, CareReport avec scénarios réalistes
- **CLI moderne** : Interface en ligne de commande avec aide intégrée (`--help`)

### **🛠️ Commandes Utiles**

```bash
# S'attacher à un conteneur spécifique pour le debug
docker attach arosa-je-api    # Pour débugger l'API
docker attach arosa-je-web    # Pour débugger le frontend
docker attach arosa-je-mobile # Pour débugger l'app mobile

# Note: Utilisez CTRL+P CTRL+Q pour se détacher sans arrêter le conteneur
```

### **⚠️ Résolution des Problèmes**

Si `bin/up all` échoue, vérifiez :
1. Que Docker est en cours d'exécution
2. Que les ports requis sont disponibles : **8000**, **3000**, **5000**, **5432**, **6379**, **3001**, **9090**, **8086**
3. Que tous les dossiers nécessaires existent (api, web, mobile, monitoring)
4. Que les Dockerfiles sont présents dans chaque dossier
5. Que les dépendances Python sont correctement installées (`bin/setup-api`)
6. Que PostgreSQL et Redis peuvent démarrer (vérifier les logs Docker)

Pour un debug détaillé :
- Utilisez `docker attach` pour vous connecter directement au conteneur
- Les logs en temps réel s'afficheront dans votre terminal
- CTRL+P CTRL+Q permet de se détacher sans arrêter le conteneur
- CTRL+C arrêtera le conteneur si vous ne vous détachez pas proprement

### **📝 Gestion des Dépendances**

#### API (Python)
```bash
# Installation d'une nouvelle dépendance
cd api
source venv/bin/activate  # ou `source venv/Scripts/activate` sur Windows
pip install nouvelle_dependance
cd ..
bin/setup-api  # Met à jour requirements.txt
```

### **🤝 Contributeurs**

- EL HAIMER Wacim
- ANNAJAR Mohamed
- AMIRI Mohammed EL-FATEH 
- BOUANANI Ryan
- AKAY Omer
