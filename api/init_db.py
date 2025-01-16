from utils.database import Base, engine

# Import des modèles pour s'assurer qu'ils sont enregistrés avec Base
from models.user import User
from models.plant import Plant
from models.photo import Photo
from models.advice import Advice
from models.plant_care import PlantCare

def init_database():
    """Initialise la base de données avec les tables"""
    print("🔧 Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données initialisée avec succès!")

if __name__ == "__main__":
    init_database() 