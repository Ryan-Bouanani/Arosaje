from pathlib import Path
import os
from sqlalchemy import create_engine, text, MetaData
import sys

# Ajouter le dossier parent (api) au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Import des modèles pour s'assurer qu'ils sont enregistrés avec Base
from utils.database import Base
from models.user import User
from models.plant import Plant
from models.photo import Photo
from models.garde import Garde
from models.advice import Advice

def check_tables(engine):
    """Vérifie les tables existantes dans la base de données"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print("Tables existantes:", tables)
    return tables

def clear_all_tables(engine):
    """Vide toutes les tables de la base de données"""
    with engine.connect() as conn:
        # Désactiver temporairement les contraintes de clé étrangère
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        
        # Récupérer toutes les tables
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        
        # Vider chaque table
        for table in tables:
            if table != "sqlite_sequence":  # Ignorer la table système
                conn.execute(text(f"DELETE FROM {table}"))
        
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()

def create_tables(engine):
    """Crée toutes les tables dans la base de données"""
    # S'assurer que tous les modèles sont importés et enregistrés
    models = [User, Plant, Photo, Garde, Advice]
    
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    # Vérifier les tables créées
    tables = check_tables(engine)
    expected_tables = {model.__tablename__ for model in models}
    
    if not all(table in tables for table in expected_tables):
        missing_tables = expected_tables - set(tables)
        raise Exception(f"Erreur: Tables manquantes: {missing_tables}")

def reset_test_database():
    """Réinitialise la base de données de test"""
    # Chemins
    TEST_DB_DIR = ROOT_DIR / "tests" / "assets" / "database"
    TEST_DB_PATH = TEST_DB_DIR / "arosaje_test.db"
    TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

    # Créer le dossier de test si nécessaire
    TEST_DB_DIR.mkdir(parents=True, exist_ok=True)

    # Supprimer l'ancienne base si elle existe
    if TEST_DB_PATH.exists():
        os.remove(TEST_DB_PATH)
        print("Ancienne base supprimée")

    # Créer le moteur SQLAlchemy
    engine = create_engine(TEST_DATABASE_URL)
    
    try:
        # Créer les tables
        create_tables(engine)
        print("Base de test créée avec succès")
        
        # Vérifier les tables
        tables = check_tables(engine)
        
    except Exception as e:
        print(f"Erreur lors de la création de la base: {str(e)}")
        raise

if __name__ == "__main__":
    reset_test_database() 