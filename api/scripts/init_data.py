from models.user import User, UserRole
from models.plant import Plant
from utils.database import SessionLocal
from utils.password import get_password_hash

def init_data():
    """Initialise les données de base (admin et plantes) si elles n'existent pas"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.id == 1).first()
        
        if not admin:
            print("🌱 Création du compte administrateur...")
            admin = User(
                id=1,
                email="root@arosa.fr",
                password=get_password_hash("epsi691"),
                nom="Admin",
                prenom="System",
                role=UserRole.ADMIN,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("✅ Compte administrateur créé avec succès")

            print("🌱 Ajout des plantes de test...")
            plantes = [
                Plant(
                    nom="Rose",
                    espece="Rosa",
                    description="La reine des fleurs, symbole d'amour et de passion. Disponible en nombreuses couleurs",
                    photo="assets/persisted_img/rose.jpg",
                    owner_id=1
                ),
                Plant(
                    nom="Orchidée Phalaenopsis",
                    espece="Phalaenopsis",
                    description="L'orchidée la plus populaire, avec ses fleurs élégantes qui durent plusieurs mois",
                    photo="assets/persisted_img/orchidee.jpg",
                    owner_id=1
                ),
                Plant(
                    nom="Tournesol",
                    espece="Helianthus annuus",
                    description="Grande fleur jaune qui suit le soleil, symbole de joie et d'été",
                    photo="assets/persisted_img/tournesol.jpg",
                    owner_id=1
                ),
                Plant(
                    nom="Lavande",
                    espece="Lavandula",
                    description="Plante aromatique méditerranéenne connue pour son parfum apaisant",
                    photo="assets/persisted_img/lavande.jpg",
                    owner_id=1
                ),
                Plant(
                    nom="Tulipe",
                    espece="Tulipa",
                    description="Fleur printanière emblématique des Pays-Bas, disponible en multiples couleurs",
                    photo="assets/persisted_img/tulipe.jpg",
                    owner_id=1
                ),
                Plant(
                    nom="Lys",
                    espece="Lilium",
                    description="Fleur majestueuse au parfum intense, symbole de pureté",
                    photo="assets/persisted_img/lys.jpg",
                    owner_id=1
                ),
                Plant(
                    nom="Marguerite",
                    espece="Leucanthemum",
                    description="Fleur simple et champêtre, symbole de l'innocence",
                    photo="assets/persisted_img/marguerite.jpg",
                    owner_id=1
                ),
                Plant(
                    nom="Jasmin",
                    espece="Jasminum",
                    description="Plante grimpante aux fleurs blanches très parfumées",
                    photo="assets/persisted_img/jasmin.jpg",
                    owner_id=1
                ),
                Plant(
                    nom="Pivoine",
                    espece="Paeonia",
                    description="Fleur volumineuse aux pétales délicats, très appréciée en bouquet",
                    photo="assets/persisted_img/pivoine.jpg",
                    owner_id=1
                ),
                Plant(
                    nom="Chrysanthème",
                    espece="Chrysanthemum",
                    description="Fleur automnale résistante, symbole de longévité dans certaines cultures",
                    photo="assets/persisted_img/chrysantheme.jpg",
                    owner_id=1
                )
            ]
            
            for plante in plantes:
                db.add(plante)
            
            db.commit()
            print("✅ Plantes de test ajoutées avec succès")
        else:
            print("ℹ️ L'administrateur existe déjà, mise à jour du mot de passe...")
            admin.password = get_password_hash("epsi691")
            admin.role = UserRole.ADMIN  # S'assurer que le rôle est bien ADMIN
            admin.is_verified = True     # S'assurer que le compte est vérifié
            db.commit()
            print("✅ Mot de passe administrateur mis à jour avec succès")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation des données : {e}")
        db.rollback()
    finally:
        db.close() 