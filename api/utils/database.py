"""Configuration de la base de données."""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://arosaje:epsi@localhost:5432/arosaje_db")

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Création du moteur
engine = create_engine(DATABASE_URL)

# Session pour la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Crée une nouvelle session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
