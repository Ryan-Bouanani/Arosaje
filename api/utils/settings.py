import os
from pathlib import Path

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///assets/database/arosaje.db")

# Configuration générale
DEBUG_MODE = True  # Désactiver en production
PROJECT_NAME = "A'rosa-je API"
VERSION = "1.0.0"

# Sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "root")  # À changer pour la prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

CORS_ORIGINS = ["*"] 
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]