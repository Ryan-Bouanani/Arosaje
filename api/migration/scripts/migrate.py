"""Script de migration de SQLite vers PostgreSQL."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import text

# Ajout du dossier parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from config.database import sqlite_engine, postgres_engine, SQLiteSession, PostgresSession
from models import Base

# Configuration du logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "migration.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_postgres_db():
    """Crée les tables dans PostgreSQL."""
    try:
        Base.metadata.create_all(postgres_engine)
        logger.info("Tables PostgreSQL créées avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables PostgreSQL: {e}")
        raise

def get_table_names():
    """Récupère la liste des tables à migrer dans l'ordre correct."""
    return [
        "users",
        "user_presence",
        "conversations",
        "conversation_participants",
        "user_typing_status",
        "plants",
        "photos",
        "advices",
        "plant_cares",
        "messages"
    ]

def migrate_table(table_name: str, sqlite_session, postgres_session):
    """Migre les données d'une table de SQLite vers PostgreSQL."""
    try:
        # Lecture des données de SQLite
        result = sqlite_session.execute(text(f"SELECT * FROM {table_name}"))
        rows = result.fetchall()
        
        if not rows:
            logger.info(f"Aucune donnée à migrer pour la table {table_name}")
            return
        
        # Récupération des noms de colonnes
        columns = result.keys()
        
        # Construction de la requête d'insertion
        columns_str = ", ".join(columns)
        values_str = ", ".join([f":{col}" for col in columns])
        insert_query = text(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})")
        
        # Migration des données
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # Conversion des valeurs entières en booléens pour certains champs
            if table_name == "users" and "is_verified" in row_dict:
                row_dict["is_verified"] = bool(row_dict["is_verified"])
            
            if table_name == "messages" and "is_read" in row_dict:
                row_dict["is_read"] = bool(row_dict["is_read"])
            
            if table_name == "user_typing_status" and "is_typing" in row_dict:
                row_dict["is_typing"] = bool(row_dict["is_typing"])
            
            postgres_session.execute(insert_query, row_dict)
        
        postgres_session.commit()
        logger.info(f"Migration réussie pour la table {table_name}: {len(rows)} lignes")
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration de la table {table_name}: {e}")
        postgres_session.rollback()
        raise

def main():
    """Fonction principale de migration."""
    start_time = datetime.now()
    logger.info("Début de la migration")
    
    try:
        # Création des tables PostgreSQL
        setup_postgres_db()
        
        # Sessions pour les deux bases de données
        sqlite_session = SQLiteSession()
        postgres_session = PostgresSession()
        
        # Migration des tables dans l'ordre
        for table_name in get_table_names():
            migrate_table(table_name, sqlite_session, postgres_session)
        
        # Fermeture des sessions
        sqlite_session.close()
        postgres_session.close()
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Migration terminée avec succès en {duration}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration: {e}")
        raise

if __name__ == "__main__":
    main() 