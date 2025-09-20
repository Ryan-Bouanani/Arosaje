#!/usr/bin/env python3
"""
Script pour créer directement les utilisateurs en production
Utilise directement SQLAlchemy pour bypasser les validations API
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from random import choice, randint

# Ajouter le répertoire courant au path
sys.path.append(str(Path(__file__).parent))

# Import des models et database
from models.plant_care import PlantCare, CareStatus
from models.advice import Advice, AdvicePriority, ValidationStatus
from models.plant import Plant
from models.user import User, UserRole
from utils.database import get_db
from sqlalchemy.orm import Session

def create_production_users(db: Session):
    """Crée les 5 comptes essentiels pour la production"""
    print("Création des 5 comptes essentiels...")

    users_data = [
        {"email": "root@arosaje.fr", "first_name": "Admin", "last_name": "Root", "role": UserRole.ADMIN},
        {"email": "botanist@arosaje.fr", "first_name": "Dr Marie", "last_name": "Botaniste", "role": UserRole.BOTANIST},
        {"email": "botanist2@arosaje.fr", "first_name": "Dr Paul", "last_name": "Expert", "role": UserRole.BOTANIST},
        {"email": "user@arosaje.fr", "first_name": "Jean", "last_name": "Propriétaire", "role": UserRole.USER},
        {"email": "gardien@arosaje.fr", "first_name": "Sophie", "last_name": "Gardienne", "role": UserRole.USER}
    ]

    created = 0
    for user_data in users_data:
        try:
            # Vérifier si l'utilisateur existe déjà
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"  Utilisateur {user_data['email']} existe déjà")
                continue

            user = User(
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                password="$2b$12$LQ3.xqvZ9k2YF9X7P8nLa.UhjB4QmYgb4rJ5K3L8N2pF7yE9VwQR.",  # epsi691
                role=user_data["role"],
                is_verified=True,
                telephone=f"+336123456{len(str(created))}{len(str(created))}",
                localisation="Lyon, France"
            )

            db.add(user)
            db.commit()
            created += 1
            print(f"  ✓ {user_data['email']} créé")

        except Exception as e:
            print(f"  ✗ Erreur {user_data['email']}: {e}")
            db.rollback()

    return created

def create_production_plants(db: Session):
    """Crée 8 plantes essentielles"""
    print("Création de 8 plantes essentielles...")

    # Trouver le propriétaire (user@arosaje.fr)
    owner = db.query(User).filter(User.email == "user@arosaje.fr").first()
    if not owner:
        print("  ✗ Propriétaire user@arosaje.fr non trouvé")
        return 0

    plants_data = [
        {"nom": "Monstera Deliciosa", "espece": "Monstera deliciosa", "description": "Plante tropicale aux feuilles perforées"},
        {"nom": "Ficus Lyrata", "espece": "Ficus lyrata", "description": "Figuier lyre aux grandes feuilles"},
        {"nom": "Sansevieria", "espece": "Sansevieria trifasciata", "description": "Langue de belle-mère, très résistante"},
        {"nom": "Pothos Doré", "espece": "Epipremnum aureum", "description": "Plante grimpante facile d'entretien"},
        {"nom": "ZZ Plant", "espece": "Zamioculcas zamiifolia", "description": "Plante ZZ, parfaite pour débutants"},
        {"nom": "Chlorophytum", "espece": "Chlorophytum comosum", "description": "Plante araignée, purificatrice d'air"},
        {"nom": "Philodendron", "espece": "Philodendron hederaceum", "description": "Philodendron à feuilles en cœur"},
        {"nom": "Dracaena", "espece": "Dracaena marginata", "description": "Dragonnier de Madagascar, très décoratif"}
    ]

    created = 0
    for plant_data in plants_data:
        try:
            plant = Plant(
                nom=plant_data["nom"],
                espece=plant_data["espece"],
                description=plant_data["description"],
                owner_id=owner.id,
                photo_base64=None  # Pas d'images pour l'instant
            )

            db.add(plant)
            db.commit()
            created += 1
            print(f"  ✓ {plant_data['nom']} créée")

        except Exception as e:
            print(f"  ✗ Erreur {plant_data['nom']}: {e}")
            db.rollback()

    return created

def create_production_cares(db: Session):
    """Crée 15 gardes variées pour les plantes"""
    print("Création de 15 gardes de plantes...")

    plants = db.query(Plant).all()
    gardien = db.query(User).filter(User.email == "gardien@arosaje.fr").first()

    if not plants or not gardien:
        print("  ✗ Pas assez de plantes ou gardien non trouvé")
        return 0

    created = 0
    for i in range(15):
        try:
            plant = choice(plants)

            # Dates variées
            start_days = randint(1, 45)
            duration = randint(7, 21)
            start_date = datetime.now() + timedelta(days=start_days)
            end_date = start_date + timedelta(days=duration)

            # Statuts variés
            statuses = [CareStatus.PENDING, CareStatus.ACCEPTED, CareStatus.IN_PROGRESS]
            status = choice(statuses)

            instructions = [
                "Arroser modérément et surveiller l'exposition à la lumière",
                "Maintenir un taux d'humidité optimal, brumiser les feuilles",
                "Vérifier l'état des feuilles et retirer celles abîmées",
                "Placer près d'une fenêtre orientée est ou ouest",
                "Surveiller les parasites et traiter si nécessaire"
            ]

            care = PlantCare(
                plant_id=plant.id,
                owner_id=plant.owner_id,
                caretaker_id=gardien.id if i % 3 == 0 else None,  # 1/3 ont un gardien
                status=status,
                start_date=start_date,
                end_date=end_date,
                care_instructions=choice(instructions),
                location="45.764043,4.835659",
                latitude=45.764043 + (randint(-100, 100) / 10000),
                longitude=4.835659 + (randint(-100, 100) / 10000)
            )

            db.add(care)
            db.commit()
            created += 1
            print(f"  ✓ Garde {i+1} créée ({care.status})")

        except Exception as e:
            print(f"  ✗ Erreur garde {i+1}: {e}")
            db.rollback()

    return created

def create_production_advice(db: Session):
    """Crée 10 conseils botaniques"""
    print("Création de 10 conseils botaniques...")

    cares = db.query(PlantCare).all()
    botanists = db.query(User).filter(User.role == UserRole.BOTANIST).all()

    if not cares or not botanists:
        print("  ✗ Pas assez de gardes ou botanistes")
        return 0

    advice_texts = [
        "Plante en excellente santé. Continuer l'arrosage actuel.",
        "Réduire l'arrosage, signes de sur-arrosage détectés.",
        "Augmenter l'exposition à la lumière pour favoriser la croissance.",
        "Fertiliser avec un engrais liquide dilué une fois par mois.",
        "Surveiller les feuilles jaunissantes, possible carence en azote.",
        "Rempoter dans un substrat plus drainant.",
        "Attention aux cochenilles sur les feuilles, traiter rapidement."
    ]

    created = 0
    for i in range(10):
        try:
            care = choice(cares)
            botanist = choice(botanists)

            priorities = [AdvicePriority.NORMAL, AdvicePriority.URGENT, AdvicePriority.FOLLOW_UP]
            statuses = [ValidationStatus.PENDING, ValidationStatus.VALIDATED]

            advice = Advice(
                plant_care_id=care.id,
                botanist_id=botanist.id,
                title="Conseil botaniste",
                content=choice(advice_texts),
                priority=choice(priorities),
                validation_status=choice(statuses),
                version=1
            )

            db.add(advice)
            db.commit()
            created += 1
            print(f"  ✓ Conseil {i+1} créé")

        except Exception as e:
            print(f"  ✗ Erreur conseil {i+1}: {e}")
            db.rollback()

    return created

def main():
    """Population complète pour la production"""
    print("🌱 Population PRODUCTION A'rosa-je")
    print("=" * 40)
    print("Création d'un écosystème complet pour les tests")

    start_time = time.time()

    try:
        db = next(get_db())

        # Créer les données essentielles
        users_created = create_production_users(db)
        plants_created = create_production_plants(db)
        cares_created = create_production_cares(db)
        advice_created = create_production_advice(db)

        duration = time.time() - start_time
        total = users_created + plants_created + cares_created + advice_created

        print(f"\n✅ Population production terminée en {duration:.2f}s !")
        print(f"   👤 Utilisateurs: {users_created}")
        print(f"   🌱 Plantes: {plants_created}")
        print(f"   🏠 Gardes: {cares_created}")
        print(f"   🌿 Conseils: {advice_created}")
        print(f"   📊 TOTAL: {total} entités")

        print(f"\n📋 Comptes créés:")
        print(f"   Admin: root@arosaje.fr / epsi691")
        print(f"   User: user@arosaje.fr / epsi691")
        print(f"   Botaniste: botanist@arosaje.fr / epsi691")
        print(f"   Botaniste2: botanist2@arosaje.fr / epsi691")
        print(f"   Gardien: gardien@arosaje.fr / epsi691")

        print(f"\n🎯 App de test: https://ryan-bouanani.github.io/Arosaje/")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    main()