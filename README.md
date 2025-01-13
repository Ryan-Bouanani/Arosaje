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

3. **Communication**  
   - Coordination entre propriétaires et gardiens via une messagerie intégrée.  

4. **Historique utilisateur**  
   - Suivi des plantes gardées ou en garde via des profils détaillés.  

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

### **Base de Données : SQLite avec SQLAlchemy**  
- Choix imposé pour le projet, optimisé avec SQLAlchemy pour une meilleure abstraction des données.  
- Portable et adapté aux projets MVP (Minimum Viable Product).  

### **Containerisation : Docker & Docker Compose**  
- Uniformisation des environnements de développement.  
- Déploiement simplifié des services backend, frontend et de la base de données.  

---

## 📋 Cahier des Charges et Livrables

### **Cahier des Charges**
- Développement d’une application mobile et web répondant aux besoins exprimés.  
- Mise en œuvre d’une architecture organisée en couches (MVC).  
- Respect des bonnes pratiques de développement logiciel.

### **Livrables**
1. Application fonctionnelle (mobile et web).  
2. Documentation technique :  
   - Résultats des benchmarks technologiques.  
   - Maquettes des interfaces.  
   - Plans de tests fonctionnels.  
3. Fichiers de containerisation pour faciliter le déploiement.

---

## 🧪 Tests Réalisés

- **Tests Unitaires** : Vérification de chaque composant individuel (backend et mobile).  
- **Tests d’Intégration** : Validation des interactions entre les différents modules.  
- **Tests Fonctionnels** : Vérification des cas d’utilisation de l’utilisateur final.  
- **Tests de Non-Régression** : Assurance que les nouvelles fonctionnalités n’impactent pas le fonctionnement existant.  

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
chmod +x bin/up bin/update bin/setup-api

# Configurer l'environnement Python pour l'API
bin/setup-api

# Démarrer tous les services
bin/up all

# Mettre à jour tous les dépôts
bin/update
```

### **🌐 Services & Ports**

| Service | Description | URL Locale | Technologies |
|---------|------------|------------|--------------|
| API | Backend API | http://localhost:8000 | FastAPI (Python) |
| Web | Interface Web | http://localhost:3000 | Vue.js (Nuxt.js) |
| Mobile | App Flutter (Web) | http://localhost:8080 | Flutter |

### **🛠️ Scripts Utilitaires**

| Script | Description | Utilisation |
|--------|------------|-------------|
| `bin/up` | Gestion des conteneurs | `bin/up all` pour démarrer la stack |
| `bin/update` | Mise à jour des dépôts | `bin/update` pour synchroniser avec main |
| `bin/setup-api` | Configuration de l'API | `bin/setup-api` pour gérer les dépendances Python |

#### Commandes Spéciales
- `CTRL+C` : Arrêter proprement tous les conteneurs
- `CTRL+R` : Redémarrer tous les conteneurs

### **📝 Documentation API**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### **⚠️ Résolution des Problèmes**

Si `bin/up all` échoue, vérifiez :
1. Que Docker est en cours d'exécution
2. Que les ports requis (8000, 3000, 8080) sont disponibles
3. Que tous les dossiers nécessaires existent (api, web, mobile)
4. Que les Dockerfiles sont présents dans chaque dossier
5. Que les dépendances Python sont correctement installées (`bin/setup-api`)

Pour des logs détaillés :
```bash
docker-compose logs [service]
```

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
- AMIRI Mohamed
- BOUANANI Ryan
- AKAY Omer