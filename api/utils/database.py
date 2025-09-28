"""Configuration de la base de données pour Neon PostgreSQL."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration de la base de données depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Configuration du moteur SQLAlchemy - adaptatif local/production
connect_args = {"application_name": "arosaje-fastapi"}

# Configuration SSL adaptative et robuste
def get_ssl_mode(database_url: str) -> str:
    """Détermine le mode SSL de façon robuste et configurable"""
    # 1. Variable explicite (priorité maximale)
    explicit_ssl = os.getenv("DB_SSL_MODE")
    if explicit_ssl:
        return explicit_ssl

    # 2. Détection automatique améliorée (fallback)
    from urllib.parse import urlparse
    parsed = urlparse(database_url)

    # Environnements locaux étendus
    local_indicators = [
        'localhost', '127.0.0.1', '::1',  # IP locales
        'db', 'postgres',  # Noms containers Docker
        '.local'  # Domaines locaux
    ]

    hostname = parsed.hostname or ""
    if any(indicator in hostname.lower() for indicator in local_indicators):
        return "disable"

    # 3. Production par défaut (sécurisé)
    return "require"

# Appliquer la configuration SSL
connect_args["sslmode"] = get_ssl_mode(DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérification de la connexion avant utilisation
    pool_recycle=300,    # Recyclage des connexions après 5 minutes
    connect_args=connect_args
)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Session pour la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Crée une nouvelle session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
