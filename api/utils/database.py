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

# Différencier local vs production basé sur l'URL
if "localhost" in DATABASE_URL or "postgres:5432" in DATABASE_URL:
    # Développement local - pas de SSL
    connect_args["sslmode"] = "disable"
else:
    # Production (Neon) - SSL requis
    connect_args["sslmode"] = "require"

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
