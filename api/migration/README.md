# Migration SQLite vers PostgreSQL

Ce dossier contient les scripts nécessaires pour migrer la base de données SQLite vers PostgreSQL.

## Structure du Projet

```
migration/
├── config/
│   └── database.py     # Configuration des connexions aux bases de données
├── scripts/
│   ├── models.py       # Modèles SQLAlchemy pour la nouvelle structure
│   └── migrate.py      # Script principal de migration
├── logs/               # Logs de migration
├── requirements.txt    # Dépendances Python
└── README.md          # Ce fichier
```

## Prérequis

1. PostgreSQL installé et en cours d'exécution
2. Python 3.8 ou supérieur
3. Base de données SQLite source existante

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
Créez un fichier `.env` dans le dossier `migration/` avec les informations suivantes :
```env
POSTGRES_USER=arosaje
POSTGRES_PASSWORD=epsi
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=arosaje_db
```

## Préparation de PostgreSQL

1. Créer la base de données :
```sql
CREATE DATABASE arosaje_db;
CREATE USER arosaje WITH PASSWORD 'epsi';
ALTER ROLE arosaje SET client_encoding TO 'utf8';
ALTER ROLE arosaje SET default_transaction_isolation TO 'read committed';
ALTER ROLE arosaje SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE arosaje_db TO arosaje;
```

## Exécution de la Migration

1. Assurez-vous que votre base SQLite source est à jour et accessible.

2. Lancez le script de migration :
```bash
cd scripts
python migrate.py
```

3. Vérifiez les logs dans le dossier `logs/` pour suivre la progression et détecter d'éventuelles erreurs.

## Structure de la Nouvelle Base de Données

La nouvelle base de données PostgreSQL suit une structure optimisée avec les tables suivantes :

- `users` : Informations des utilisateurs
- `user_presence` : Statut de présence des utilisateurs
- `user_typing_status` : État de frappe dans les conversations
- `plants` : Informations sur les plantes
- `photos` : Photos des plantes
- `advices` : Conseils botaniques
- `plant_cares` : Sessions de garde de plantes
- `conversations` : Conversations entre utilisateurs
- `messages` : Messages dans les conversations
- `conversation_participants` : Participants aux conversations

## En Cas de Problème

1. Vérifiez les logs dans le dossier `logs/`
2. Assurez-vous que les deux bases de données sont accessibles
3. Vérifiez les permissions PostgreSQL
4. En cas d'erreur pendant la migration, la transaction sera annulée automatiquement

## Notes Importantes

- La migration est transactionnelle : en cas d'erreur, toutes les modifications sont annulées
- Les données sont migrées dans un ordre spécifique pour respecter les contraintes de clés étrangères
- Les identifiants sont préservés lors de la migration
- Les index et contraintes sont recréés automatiquement dans PostgreSQL 