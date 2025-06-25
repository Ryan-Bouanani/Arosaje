"""Script d'initialisation des données."""
import os
import sys

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user import User, UserRole
from models.plant import Plant
from utils.database import SessionLocal
from utils.password import get_password_hash

def init_data():
    """Initialise les données de base (admin et plantes)."""
    db = SessionLocal()
    try:
        # Créer les utilisateurs de base
        admin = User(
            email="root@arosaje.fr",
            password=get_password_hash("epsi691"),
            nom="Admin",
            prenom="System",
            role=UserRole.ADMIN,
            is_verified=True
        )
        db.add(admin)
        db.flush()  # Pour obtenir l'ID de l'admin

        test_user = User(
            email="user@arosaje.fr",
            password=get_password_hash("epsi691"),
            nom="Test",
            prenom="User",
            role=UserRole.USER,
            is_verified=True
        )
        db.add(test_user)
        db.flush()  # Pour obtenir l'ID du test_user

        test_botanist = User(
            email="botanist@arosaje.fr",
            password=get_password_hash("epsi691"),
            nom="Botanist",
            prenom="Test",
            role=UserRole.BOTANIST,
            is_verified=True
        )
        db.add(test_botanist)
        db.flush()  # Pour obtenir l'ID du botanist

        # Créer les plantes de test
        plantes = [
            Plant(
                nom="Rose",
                espece="Rosa",
                description="La reine des fleurs, symbole d'amour et de passion. Disponible en nombreuses couleurs",
                photo="assets/persisted_img/rose.jpg",
                owner_id=test_user.id  # Utiliser l'ID généré automatiquement
            ),
            Plant(
                nom="Orchidée Phalaenopsis",
                espece="Phalaenopsis",
                description="L'orchidée la plus populaire, avec ses fleurs élégantes qui durent plusieurs mois",
                photo="assets/persisted_img/orchidee.jpg",
                owner_id=test_user.id
            ),
            Plant(
                nom="Tournesol",
                espece="Helianthus annuus",
                description="Grande fleur jaune qui suit le soleil, symbole de joie et d'été",
                photo="assets/persisted_img/tournesol.jpg",
                owner_id=test_user.id
            ),
            Plant(
                nom="Lavande",
                espece="Lavandula",
                description="Plante aromatique méditerranéenne connue pour son parfum apaisant",
                photo="assets/persisted_img/lavande.jpg",
                owner_id=test_user.id
            ),
            Plant(
                nom="Tulipe",
                espece="Tulipa",
                description="Fleur printanière emblématique des Pays-Bas, disponible en multiples couleurs",
                photo="assets/persisted_img/tulipe.jpg",
                owner_id=test_user.id
            )
        ]
        
        for plante in plantes:
            db.add(plante)
        
        db.commit()
        print("✅ Données de base créées avec succès")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation des données : {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_data() 