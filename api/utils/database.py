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

# Configuration du moteur SQLAlchemy pour Neon avec SSL
engine = create_engine(
    DATABASE_URL,
    # Configuration pour Neon PostgreSQL
    pool_pre_ping=True,  # Vérification de la connexion avant utilisation
    pool_recycle=300,    # Recyclage des connexions après 5 minutes
    connect_args={
        "sslmode": "require",
        "application_name": "arosaje-fastapi"
    }
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
