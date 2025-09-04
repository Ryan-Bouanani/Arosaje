# 🔒 Guide de Sécurité - A'rosa-je

## Vue d'ensemble

Ce document décrit les bonnes pratiques de sécurité implémentées dans l'application A'rosa-je et les recommandations pour un déploiement sécurisé.

## 🔐 Configuration des Variables d'Environnement

### Structure des Fichiers

```
📁 Projet/
├── .env.example              # Template principal
├── env/
│   ├── .env.api.example     # Configuration API
│   ├── .env.mobile.example  # Configuration Mobile
│   └── .env.web.example     # Configuration Web
└── secrets/
    └── *.env.example        # Templates pour secrets SMTP, etc.
```

### Initialisation Sécurisée

1. **Copiez les templates**:
   ```bash
   cp .env.example .env
   cp env/.env.api.example env/.env.api
   cp env/.env.mobile.example env/.env.mobile
   ```

2. **Configurez les valeurs sensibles** (voir sections ci-dessous)

3. **Vérifiez les permissions**:
   ```bash
   chmod 600 .env env/.env.*
   ```

## 🔑 Variables Critiques à Sécuriser

### JWT et Authentification

```bash
# ⚠️ OBLIGATOIRE: Changez cette clé en production
JWT_SECRET_KEY=générez-une-clé-forte-de-32-caractères-minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Génération de clé sécurisée**:
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

### Base de Données

```bash
# Production PostgreSQL
DATABASE_URL=postgresql://user:motdepasse@host:5432/database

# ⚠️ Bonnes pratiques:
# - Utilisez des mots de passe forts (16+ caractères)
# - Créez un utilisateur dédié avec privilèges minimaux
# - Activez SSL/TLS pour les connexions distantes
```

### Configuration Email

```bash
# Gmail avec App Password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre.email@gmail.com
SMTP_PASSWORD=mot-de-passe-application-16-caracteres

# ⚠️ N'utilisez JAMAIS votre mot de passe Gmail principal
```

## 🛡️ Sécurité de l'Application

### Authentification et Autorisation

#### Rôles Utilisateurs
- **USER**: Propriétaires et gardiens de plantes
- **BOTANIST**: Experts pouvant donner des conseils
- **ADMIN**: Administration complète du système

#### Contrôles d'Accès
```python
# Exemple d'endpoint sécurisé
@router.get("/admin/users")
async def get_users(current_user: User = Depends(get_current_admin)):
    # Seuls les admins peuvent accéder
```

### Validation des Données

#### Upload de Fichiers
- **Validation MIME**: Vérification des magic bytes
- **Taille limitée**: Maximum 10MB par fichier
- **Types autorisés**: JPG, JPEG, PNG, GIF uniquement
- **Sanitisation**: Noms de fichiers nettoyés

```python
# Validation sécurisée des images
ALLOWED_SIGNATURES = {
    b'\\xff\\xd8\\xff': ['.jpg', '.jpeg'],  # JPEG
    b'\\x89\\x50\\x4e\\x47': ['.png'],      # PNG
}
```

### Protection Contre les Attaques

#### CORS (Cross-Origin Resource Sharing)
```python
# Configuration restrictive
CORS_ORIGINS = [
    "https://votre-domaine.com",
    "https://app.votre-domaine.com"
]
```

#### Protection des Mots de Passe
- **Hachage bcrypt** avec salt automatique
- **Vérification de complexité** côté client
- **Limite de tentatives** de connexion

## 🚀 Déploiement Sécurisé

### Environnements

#### Développement
```bash
DEBUG=true
ENVIRONMENT=development
DATABASE_URL=sqlite:///local.db
```

#### Staging
```bash
DEBUG=false
ENVIRONMENT=staging
DATABASE_URL=postgresql://staging_user:pass@staging-db:5432/db
```

#### Production
```bash
DEBUG=false
ENVIRONMENT=production
DATABASE_URL=postgresql://prod_user:secure_pass@prod-db:5432/db
ENABLE_HTTPS=true
```

### Configuration SSL/TLS

#### Nginx (Recommandé)
```nginx
server {
    listen 443 ssl;
    server_name votre-domaine.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

#### Headers de Sécurité
```python
# FastAPI middleware
app.add_middleware(
    HTTPSRedirectMiddleware
)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["votre-domaine.com"]
)
```

## 📊 Monitoring et Logs

### Logs de Sécurité

```bash
# Configuration des logs
LOG_LEVEL=INFO
LOG_FILE=logs/security.log

# Events à surveiller:
# - Tentatives de connexion échouées
# - Accès aux endpoints sensibles
# - Upload de fichiers suspects
# - Modifications de données critiques
```

### Métriques de Sécurité

- Nombre de tentatives de connexion par IP
- Taux d'échec d'authentification
- Volume d'uploads par utilisateur
- Accès aux endpoints admin

## ⚠️ Checklist de Sécurité

### Avant le Déploiement

- [ ] **Variables d'environnement**: Toutes les clés secrètes sont changées
- [ ] **Base de données**: Utilisateur dédié avec privilèges minimaux
- [ ] **HTTPS**: Certificat SSL/TLS configuré
- [ ] **CORS**: Domaines autorisés configurés
- [ ] **Logs**: Monitoring de sécurité activé
- [ ] **Backup**: Stratégie de sauvegarde des données
- [ ] **Updates**: Dépendances à jour avec patches de sécurité

### Maintenance Continue

- [ ] **Rotation des clés**: Changement périodique des secrets
- [ ] **Audit des logs**: Vérification régulière des accès
- [ ] **Mises à jour**: Dépendances et système d'exploitation
- [ ] **Tests de pénétration**: Audit de sécurité périodique

## 🆘 Réponse aux Incidents

### En cas de Compromission

1. **Isolement**: Couper l'accès aux systèmes compromis
2. **Investigation**: Analyser les logs pour identifier l'ampleur
3. **Rotation**: Changer immédiatement toutes les clés secrètes
4. **Communication**: Notifier les utilisateurs si nécessaire
5. **Correction**: Appliquer les correctifs nécessaires
6. **Surveillance**: Monitoring renforcé post-incident

### Contacts d'Urgence

- **Équipe DevOps**: devops@arosaje.com
- **Responsable Sécurité**: security@arosaje.com
- **Direction Technique**: cto@arosaje.com

## 📚 Ressources et Standards

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)

---

**Dernière mise à jour**: Septembre 2024  
**Version**: 1.0  
**Maintenu par**: Équipe Développement A'rosa-je