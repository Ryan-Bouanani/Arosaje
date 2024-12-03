
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

---
