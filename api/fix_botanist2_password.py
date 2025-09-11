#!/usr/bin/env python3
"""
Script pour corriger le mot de passe de botanist2@arosaje.fr
"""

import sys
import os
sys.path.append('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User
from utils.settings import settings
from passlib.context import CryptContext

# Configuration du hashage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de la base de données
DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_botanist2_password():
    """Corriger le mot de passe de botanist2@arosaje.fr"""
    db = SessionLocal()
    
    try:
        # Trouver l'utilisateur botanist2
        user = db.query(User).filter(User.email == "botanist2@arosaje.fr").first()
        if not user:
            print("❌ Utilisateur botanist2@arosaje.fr introuvable")
            return
            
        # Générer un nouveau hash pour le mot de passe 'epsi691'
        new_password_hash = pwd_context.hash("epsi691")
        
        # Mettre à jour le mot de passe
        user.hashed_password = new_password_hash
        db.commit()
        
        print(f"✅ Mot de passe de {user.email} corrigé avec succès")
        print(f"   Nouveau hash: {new_password_hash[:50]}...")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_botanist2_password()