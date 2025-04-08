from models.user import User, UserRole
from models.plant import Plant
from utils.database import SessionLocal
from utils.password import get_password_hash

def init_data():
    """Initialise les données de base (admin et plantes) si elles n'existent pas"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.id == 1).first()
        test_user = db.query(User).filter(User.id == 2).first()
        test_botanist = db.query(User).filter(User.id == 3).first()
        
        if not admin:
            print("🌱 Création du compte administrateur...")
            admin = User(
                id=1,
                email="root@arosaje.fr",
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

        if not test_user:
            print("🌱 Création du compte de test...")
            test_user = User(
                id=2,
                email="user@arosaje.fr", 
                password=get_password_hash("epsi691"),
                nom="Test",
                prenom="User",
                role=UserRole.USER,
                is_verified=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print("✅ Compte de test créé avec succès")

        if not test_botanist:
            print("🌱 Création du compte de botaniste...")
            test_botanist = User(
                id=3,
                email="botanist@arosaje.fr",
                password=get_password_hash("epsi691"),
                nom="Botanist",
                prenom="Test",
                role=UserRole.BOTANIST,
                is_verified=True
            )
            db.add(test_botanist)
            db.commit()
            db.refresh(test_botanist)
            print("✅ Compte de test botaniste créé avec succès")
            
            print("🌱 Ajout des plantes de test...")
            plantes = [
                Plant(
                    nom="Rose",
                    espece="Rosa",
                    description="La reine des fleurs, symbole d'amour et de passion. Disponible en nombreuses couleurs",
                    photo="assets/persisted_img/rose.jpg",
                    owner_id=2
                ),
                Plant(
                    nom="Orchidée Phalaenopsis",
                    espece="Phalaenopsis",
                    description="L'orchidée la plus populaire, avec ses fleurs élégantes qui durent plusieurs mois",
                    photo="assets/persisted_img/orchidee.jpg",
                    owner_id=2
                ),
                Plant(
                    nom="Tournesol",
                    espece="Helianthus annuus",
                    description="Grande fleur jaune qui suit le soleil, symbole de joie et d'été",
                    photo="assets/persisted_img/tournesol.jpg",
                    owner_id=2
                ),
                Plant(
                    nom="Lavande",
                    espece="Lavandula",
                    description="Plante aromatique méditerranéenne connue pour son parfum apaisant",
                    photo="assets/persisted_img/lavande.jpg",
                    owner_id=2
                ),
                Plant(
                    nom="Tulipe",
                    espece="Tulipa",
                    description="Fleur printanière emblématique des Pays-Bas, disponible en multiples couleurs",
                    photo="assets/persisted_img/tulipe.jpg",
                    owner_id=2
                ),
                Plant(
                    nom="Lys",
                    espece="Lilium",
                    description="Fleur majestueuse au parfum intense, symbole de pureté",
                    photo="assets/persisted_img/lys.jpg",
                    owner_id=2
                ),
                Plant(
                    nom="Marguerite",
                    espece="Leucanthemum",
                    description="Fleur simple et champêtre, symbole de l'innocence",
                    photo="assets/persisted_img/marguerite.jpg",
                    owner_id=2
                ),
                Plant(
                    nom="Jasmin",
                    espece="Jasminum",
                    description="Plante grimpante aux fleurs blanches très parfumées",
                    photo="assets/persisted_img/jasmin.jpg",
                    owner_id=2
                ),
                Plant(
                    nom="Pivoine",
                    espece="Paeonia",
                    description="Fleur volumineuse aux pétales délicats, très appréciée en bouquet",
                    photo="assets/persisted_img/pivoine.jpg",
                    owner_id=2
                ),
                Plant(
                    nom="Chrysanthème",
                    espece="Chrysanthemum",
                    description="Fleur automnale résistante, symbole de longévité dans certaines cultures",
                    photo="assets/persisted_img/chrysantheme.jpg",
                    owner_id=2
                )
            ]
            
            for plante in plantes:
                db.add(plante)
            
            db.commit()
            print("✅ Plantes de test ajoutées avec succès")
        else:
            print("ℹ️ Les utilisateurs existent déjà, mise à jour des mots de passe...")
            
            # Mise à jour admin
            admin.password = get_password_hash("epsi691")
            admin.role = UserRole.ADMIN  # S'assurer que le rôle est bien ADMIN
            admin.is_verified = True     # S'assurer que le compte est vérifié
            
            # Mise à jour user standard
            test_user.password = get_password_hash("epsi691") 
            test_user.role = UserRole.USER
            test_user.is_verified = True
            
            # Mise à jour botaniste
            test_botanist.password = get_password_hash("epsi691")
            test_botanist.role = UserRole.BOTANIST
            test_botanist.is_verified = True
            
            db.commit()
            print("✅ Mots de passe des utilisateurs mis à jour avec succès")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation des données : {e}")
        db.rollback()
    finally:
        db.close() 