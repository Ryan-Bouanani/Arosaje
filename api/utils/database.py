from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Chemin de base du projet
ROOT_DIR = Path(__file__).resolve().parent.parent

# Configuration de la base de données
DB_PATH = ROOT_DIR / "assets" / "database" / "arosaje.db"

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Création du moteur
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)

# Session pour la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Crée une nouvelle session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
