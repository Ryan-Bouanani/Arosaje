from models.plant import Plant
from utils.database import SessionLocal

def seed_plants():
    db = SessionLocal()
    
    plantes = [
        Plant(
            nom="Rose",
            espece="Rosa",
            description="La reine des fleurs, symbole d'amour et de passion. Disponible en nombreuses couleurs",
            photo="assets/persisted_img/rose.jpg"
        ),
        Plant(
            nom="Orchidée Phalaenopsis",
            espece="Phalaenopsis",
            description="L'orchidée la plus populaire, avec ses fleurs élégantes qui durent plusieurs mois",
            photo="assets/persisted_img/orchidee.jpg"
        ),
        Plant(
            nom="Tournesol",
            espece="Helianthus annuus",
            description="Grande fleur jaune qui suit le soleil, symbole de joie et d'été",
            photo="assets/persisted_img/tournesol.jpg"
        ),
        Plant(
            nom="Lavande",
            espece="Lavandula",
            description="Plante aromatique méditerranéenne connue pour son parfum apaisant",
            photo="assets/persisted_img/lavande.jpg"
        ),
        Plant(
            nom="Tulipe",
            espece="Tulipa",
            description="Fleur printanière emblématique des Pays-Bas, disponible en multiples couleurs",
            photo="assets/persisted_img/tulipe.jpg"
        ),
        Plant(
            nom="Lys",
            espece="Lilium",
            description="Fleur majestueuse au parfum intense, symbole de pureté",
            photo="assets/persisted_img/lys.jpg"
        ),
        Plant(
            nom="Marguerite",
            espece="Leucanthemum",
            description="Fleur simple et champêtre, symbole de l'innocence",
            photo="assets/persisted_img/marguerite.jpg"
        ),
        Plant(
            nom="Jasmin",
            espece="Jasminum",
            description="Plante grimpante aux fleurs blanches très parfumées",
            photo="assets/persisted_img/jasmin.jpg"
        ),
        Plant(
            nom="Pivoine",
            espece="Paeonia",
            description="Fleur volumineuse aux pétales délicats, très appréciée en bouquet",
            photo="assets/persisted_img/pivoine.jpg"
        ),
        Plant(
            nom="Chrysanthème",
            espece="Chrysanthemum",
            description="Fleur automnale résistante, symbole de longévité dans certaines cultures",
            photo="assets/persisted_img/chrysantheme.jpg"
        )
    ]
    
    for plante in plantes:
        db.add(plante)
    
    try:
        db.commit()
        print("✅ Données de test des plantes ajoutées avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des données de test: {e}")
        db.rollback()
    finally:
        db.close() 