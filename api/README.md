# 🚀 API A'rosa-je

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre système :

- **Python 3.9+**
- **pip** (gestionnaire de paquets Python)

---

## 🛠️ Installation

1. Créez et activez un environnement virtuel (optionnel mais recommandé) :
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

2. Installez les dépendances requises à partir du fichier `requirements.txt` :
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Lancer le serveur

1. Démarrez le serveur FastAPI :
   ```bash
   uvicorn main:app --reload
   ```

2. Accédez au serveur local :
   - **Base URL** : [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📖 Documentation de l'API

FastAPI génère automatiquement une documentation interactive pour votre API.

- **Swagger UI** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc** : [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🛠️ Développement

Pendant le développement, utilisez l'environnement virtuel pour garantir que toutes les dépendances sont isolées.

1. Activez l'environnement virtuel :
   ```bash
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

2. Développez et testez vos modifications.

3. Désactivez l'environnement virtuel une fois terminé :
   ```bash
   deactivate
   ```

## 🧪 Tests

Pour exécuter les tests de l'API, suivez ces étapes :

1. Activez l'environnement virtuel si ce n'est pas déjà fait :
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

2. Installez les dépendances de test :
   ```bash
   pip install -r requirements-test.txt
   ```

3. Lancez le serveur FastAPI :
   ```bash
   uvicorn main:app --reload
   ```
   ou via script bin/up
   ```bash
   bin/up api
   ```

4. Lancez les tests :
   ```bash
   pytest tests/<test_name>.tavern.yaml -v
   ```

Ou alors, utilisez simplement l'IDE de votre choix, comme VSCode par exemple, et lancez les tests avec le bouton Run Tests.

Les tests utilisent Tavern, un framework de test d'API qui permet de tester facilement les endpoints HTTP. Les tests vérifient :
- L'inscription des utilisateurs
- L'authentification
- La gestion des erreurs
- La validation des données

### 🚀 Script de test automatisé

Pour simplifier l'exécution des tests, un script shell est disponible :

```bash
# Exécuter tous les tests
./tests/run_tests.sh

# Exécuter un test spécifique
./tests/run_tests.sh tests/workflows/test_auth_workflow.tavern.yaml
```

Ce script démarre automatiquement l'API si nécessaire, configure les variables d'environnement et exécute les tests.

## 🔄 Intégration continue (CI)

Les tests sont automatiquement exécutés via GitHub Actions à chaque pull request et à chaque push sur les branches `main` et `develop`.

Le workflow de CI effectue les actions suivantes :
1. Démarrage des services PostgreSQL et Redis
2. Installation des dépendances
3. Démarrage de l'API
4. Exécution des tests Tavern

Pour configurer le CI dans votre fork, aucune configuration supplémentaire n'est nécessaire car les workflows sont inclus dans le dépôt.

---
