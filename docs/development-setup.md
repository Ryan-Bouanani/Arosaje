# 🛠️ Configuration de l'environnement de développement

## 📋 Configuration rapide

1. **Copiez le template d'environnement :**
   ```bash
   cp .env.example .env
   ```

2. **Remplacez les valeurs par les configurations de développement :**

### 🗄️ Base de données (PostgreSQL local)
```bash
DATABASE_URL=postgresql://arosaje:epsi@localhost:5432/arosaje_db
```

### 🎯 Application
```bash
APP_NAME=Arosa-je
```

### 🔐 Redis (sans mot de passe en local)
```bash
REDIS_PASSWORD=
```

### 📧 Email (optionnel pour le développement)
```bash
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app-gmail
```

## 🚀 Démarrage automatique

**Méthode recommandée :** Utilisez le script de configuration automatique
```bash
./bin/setup-env
```

Ce script génère automatiquement tous les fichiers `.env` avec les bonnes configurations et des secrets sécurisés.

## 📁 Structure des fichiers d'environnement

```
├── .env.example          # Template générique (ce fichier)
├── env/
│   ├── .env.api         # Configuration API (généré automatiquement)
│   ├── .env.web         # Configuration frontend web
│   └── .env.mobile      # Configuration mobile Flutter
```

## ⚠️ Important

- **NE JAMAIS** committer les fichiers `.env` réels
- Les fichiers `.env` contiennent des secrets et sont ignorés par Git
- Utilisez toujours `./bin/setup-env` pour la première configuration