#!/usr/bin/env python3
"""
Script pour initialiser la base de données locale avec les comptes essentiels
"""

import sys
import os
import hashlib

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User
from models.plant import Plant
from models.plant_care import PlantCare

# Utiliser DATABASE_URL locale
DATABASE_URL = "postgresql://arosaje:epsi@localhost:5433/arosaje_db?sslmode=disable"

def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_local_dev():
    """Initialise la base locale avec les comptes essentiels"""
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        db = SessionLocal()

        print("=== INITIALISATION BASE DE DONNÉES LOCALE ===\n")

        # Vérifier si des users existent déjà
        existing_users = db.query(User).count()
        print(f"Utilisateurs existants: {existing_users}")

        if existing_users > 0:
            print("Base déjà initialisée - aucune action nécessaire")
            return

        # Créer les comptes essentiels
        users_to_create = [
            {
                "email": "root@arosaje.fr",
                "password": "epsi691",
                "first_name": "Admin",
                "last_name": "Root",
                "role": "ADMIN",
                "is_verified": True
            },
            {
                "email": "user@arosaje.fr",
                "password": "epsi691",
                "first_name": "Jean",
                "last_name": "Dupont",
                "role": "USER",
                "is_verified": True
            },
            {
                "email": "gardien@arosaje.fr",
                "password": "epsi691",
                "first_name": "Sophie",
                "last_name": "Martin",
                "role": "USER",
                "is_verified": True
            },
            {
                "email": "botanist@arosaje.fr",
                "password": "epsi691",
                "first_name": "Dr. Pierre",
                "last_name": "Botanicus",
                "role": "BOTANIST",
                "is_verified": True
            }
        ]

        print("Création des comptes essentiels:")
        for user_data in users_to_create:
            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                is_verified=user_data["is_verified"]
            )
            db.add(user)
            print(f"  + {user_data['email']} ({user_data['role']})")

        db.commit()

        print(f"\n✅ Base locale initialisée avec {len(users_to_create)} comptes")
        print("Vous pouvez maintenant utiliser l'API en local !")

        db.close()

    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_local_dev()