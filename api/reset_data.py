#!/usr/bin/env python3
"""
Script pour reset les données (plantes, gardes, conseils, conversations)
tout en conservant les comptes utilisateurs
"""

import sys
import os
sys.path.append('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.message import Message, Conversation, ConversationParticipant
from models.advice import Advice
from models.care_report import CareReport
from models.plant_care import PlantCare
from models.plant import Plant
from utils.settings import settings

# Configuration de la base de données
DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reset_data():
    """Reset toutes les données sauf les comptes utilisateurs"""
    db = SessionLocal()
    
    try:
        print('🗑️ Suppression des conversations et messages...')
        deleted_messages = db.query(Message).delete()
        deleted_participants = db.query(ConversationParticipant).delete()
        deleted_conversations = db.query(Conversation).delete()
        print(f'   - {deleted_messages} messages supprimés')
        print(f'   - {deleted_participants} participants supprimés')
        print(f'   - {deleted_conversations} conversations supprimées')
        
        print('🗑️ Suppression des conseils botaniques...')
        deleted_advice = db.query(Advice).delete()
        print(f'   - {deleted_advice} conseils supprimés')
        
        print('🗑️ Suppression des rapports de garde...')
        deleted_reports = db.query(CareReport).delete()
        print(f'   - {deleted_reports} rapports supprimés')
        
        print('🗑️ Suppression des gardes de plantes...')
        deleted_cares = db.query(PlantCare).delete()
        print(f'   - {deleted_cares} gardes supprimées')
        
        print('🗑️ Suppression des plantes...')
        deleted_plants = db.query(Plant).delete()
        print(f'   - {deleted_plants} plantes supprimées')
        
        # Commit les changements
        db.commit()
        print('✅ Reset terminé avec succès !')
        print('ℹ️ Comptes utilisateurs conservés')
        
    except Exception as e:
        db.rollback()
        print(f'❌ Erreur: {e}')
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_data()