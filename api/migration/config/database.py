"""Configuration des bases de données source et cible."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Configuration SQLite (source)
SQLITE_DB_PATH = Path(__file__).parent.parent.parent / "assets" / "database" / "arosaje.db"
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"
sqlite_engine = create_engine(SQLITE_URL)
SQLiteSession = sessionmaker(bind=sqlite_engine)

# Configuration PostgreSQL (cible)
POSTGRES_USER = "arosaje"
POSTGRES_PASSWORD = "epsi"  # À changer en production
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "arosaje_db"

POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
postgres_engine = create_engine(POSTGRES_URL)
PostgresSession = sessionmaker(bind=postgres_engine) 