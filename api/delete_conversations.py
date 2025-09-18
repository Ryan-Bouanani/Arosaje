#!/usr/bin/env python3
import os
import sys

# Ajouter le répertoire API au path
sys.path.append('/app')

from models.message import Conversation, Message
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

def delete_all_conversations():
    try:
        # Connexion à la base
        engine = create_engine(os.getenv('DATABASE_URL'))
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        # Afficher les conversations existantes
        conversations = db.query(Conversation).all()
        print('Conversations existantes:')
        for conv in conversations:
            print(f'ID: {conv.id}, User1: {conv.user1_id}, User2: {conv.user2_id}, Type: {conv.conversation_type}, Related: {conv.related_id}')

        # Supprimer d'abord tous les messages
        messages_deleted = db.query(Message).delete()
        print(f'Messages supprimés: {messages_deleted}')

        # Ensuite supprimer toutes les conversations
        conversations_deleted = db.query(Conversation).delete()
        db.commit()

        print(f'Conversations supprimées: {conversations_deleted}')
        print('Toutes les conversations ont été supprimées avec succès!')

    except Exception as e:
        print(f'Erreur: {e}')
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    delete_all_conversations()