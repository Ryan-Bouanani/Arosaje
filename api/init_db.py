from utils.database import Base, engine
from models import user, plant, advice, garde, photo
import os
from pathlib import Path
from utils.settings import DATABASE_URL
import sqlite3

def check_sqlite_db():
    """Vérifie si la base de données SQLite est valide"""
    try:
        # Extraire le chemin du fichier de l'URL SQLite
        db_path = DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_path):
            # Tester la connexion à la base de données
            conn = sqlite3.connect(db_path)
            conn.close()
            return True
    except sqlite3.Error:
        return False
    return False

def init_db():
    # Vérifier si l'URL est bien pour SQLite
    if not DATABASE_URL.startswith("sqlite:///"):
        print("❌ Erreur: La configuration attend une base de données SQLite")
        return False

    # Créer le dossier database s'il n'existe pas
    db_path = Path("assets/database")
    db_path.mkdir(parents=True, exist_ok=True)
    
    # Vérifier si la base de données existe déjà et est valide
    if check_sqlite_db():
        print("ℹ️ La base de données existe déjà et semble valide")
        return True
    
    try:
        print("🔧 Création des tables dans la base de données...")
        Base.metadata.create_all(bind=engine)
        
        # Vérifier que la base de données a été créée correctement
        if check_sqlite_db():
            print("✅ Base de données initialisée avec succès!")
            return True
        else:
            print("❌ Erreur: La base de données n'a pas pu être créée correctement")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base de données: {str(e)}")
        return False

if __name__ == "__main__":
    init_db() 