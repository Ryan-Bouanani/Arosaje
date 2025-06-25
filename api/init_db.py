"""Initialisation de la base de données."""
from utils.database import Base, engine
from models.user import User
from models.plant import Plant
from models.plant_care import PlantCare
from models.photo import Photo
from models.advice import Advice
from models.message import Conversation, ConversationParticipant, Message

def create_tables():
    """Crée toutes les tables dans la base de données."""
    print("🔧 Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès!")

def drop_tables():
    """Supprime toutes les tables de la base de données."""
    print("🗑️ Suppression des tables existantes...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables supprimées avec succès!")

def init_database(reset=False):
    """Initialise la base de données avec les tables.
    
    Args:
        reset (bool): Si True, supprime toutes les tables avant de les recréer.
    """
    if reset:
        drop_tables()
    create_tables()

if __name__ == "__main__":
    import sys
    reset = "--reset" in sys.argv
    init_database(reset=reset) 