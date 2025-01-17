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

# Configuration Redis
REDIS_HOST = os.getenv("REDIS_HOST", "api-redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")

# Configuration CORS
CORS_ALLOW_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://web:3000,http://localhost:5000,http://mobile:5000").split(",")
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
CORS_ALLOW_HEADERS = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
    "X-Requested-With",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers"
]