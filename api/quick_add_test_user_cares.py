#!/usr/bin/env python3
"""
Script pour ajouter des gardes spécifiquement pour user@arosaje.fr
et compléter à 60 gardes total
"""

import sys
import os
from pathlib import Path
import random
from datetime import datetime, timedelta

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

# Configuration database
from factories.base import SessionLocal
from models.user import User, UserRole
from models.plant import Plant
from models.plant_care import PlantCare, CareStatus
from sqlalchemy import text

def get_city_coordinates(location):
    """Retourne coordonnées GPS avec dispersion pour simulation quartiers"""

    # Coordonnées centres + dispersion par ville
    city_coords = {
        'Paris, France': (48.8566, 2.3522, 0.1),
        'Lyon, France': (45.7640, 4.8357, 0.08),
        'Marseille, France': (43.2965, 5.3698, 0.08),
        'Toulouse, France': (43.6047, 1.4442, 0.08),
        'Nice, France': (43.7102, 7.2620, 0.06),
        'Nantes, France': (47.2184, -1.5536, 0.06),
        'Montpellier, France': (43.6110, 3.8767, 0.06),
        'Strasbourg, France': (48.5734, 7.7521, 0.06),
        'Bordeaux, France': (44.8378, -0.5792, 0.08),
        'Lille, France': (50.6292, 3.0573, 0.06)
    }

    # Récupérer coordonnées de base ou utiliser Paris par défaut
    lat_base, lng_base, dispersion = city_coords.get(
        location,
        (48.8566, 2.3522, 0.1)  # Paris par défaut
    )

    # Ajouter dispersion aléatoire pour simuler différents quartiers
    lat_offset = (random.random() - 0.5) * dispersion
    lng_offset = (random.random() - 0.5) * dispersion

    return (
        round(lat_base + lat_offset, 6),
        round(lng_base + lng_offset, 6)
    )

def add_test_user_plant_cares():
    """Ajouter des gardes pour user@arosaje.fr et compléter à 60 total"""
    print("Ajout de gardes pour user@arosaje.fr et completion a 60 total...")
    session = SessionLocal()

    try:
        # 1. Vérifier user@arosaje.fr (ID: 2)
        test_user = session.query(User).filter(User.email == 'user@arosaje.fr').first()
        if not test_user:
            print("ERREUR: user@arosaje.fr non trouve")
            return False

        print(f"User trouve: {test_user.first_name} {test_user.last_name} (ID: {test_user.id})")

        # 2. Créer 3 plantes pour user@arosaje.fr
        print("Creation de 3 plantes pour user@arosaje.fr...")

        plant_data = [
            {
                'nom': 'Monstera Deliciosa de Test',
                'espece': 'Monstera deliciosa',
                'description': 'Plante de test pour user@arosaje.fr - Monstera',
                'photo_before_base64': '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/',
                'photo_after_base64': '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/'
            },
            {
                'nom': 'Ficus Lyrata de Test',
                'espece': 'Ficus lyrata',
                'description': 'Plante de test pour user@arosaje.fr - Ficus',
                'photo_before_base64': '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/',
                'photo_after_base64': '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/'
            },
            {
                'nom': 'Pothos Doré de Test',
                'espece': 'Epipremnum aureum',
                'description': 'Plante de test pour user@arosaje.fr - Pothos',
                'photo_before_base64': '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/',
                'photo_after_base64': '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/'
            }
        ]

        test_user_plants = []
        for plant_info in plant_data:
            plant = Plant(
                nom=plant_info['nom'],
                name=plant_info['nom'],
                espece=plant_info['espece'],
                species=plant_info['espece'],
                description=plant_info['description'],
                photo_base64=plant_info['photo_before_base64'],
                owner_id=test_user.id
            )
            session.add(plant)
            test_user_plants.append(plant)

        session.commit()
        print(f"  OK {len(test_user_plants)} plantes creees pour user@arosaje.fr")

        # 3. Récupérer tous les utilisateurs pour les gardes
        all_users = session.query(User).all()
        all_plants = session.query(Plant).all()

        print(f"Users disponibles: {len(all_users)}, Plantes disponibles: {len(all_plants)}")

        # 4. Vérifier le nombre actuel de gardes
        current_care_count = session.query(PlantCare).count()
        print(f"Gardes actuelles: {current_care_count}")

        target_total = 60
        cares_to_add = target_total - current_care_count
        print(f"Gardes a ajouter: {cares_to_add}")

        # 5. Créer des gardes pour user@arosaje.fr (5 gardes comme propriétaire + 3 comme gardien)
        print("Creation de gardes pour user@arosaje.fr...")

        # A) Gardes où user@arosaje.fr est propriétaire (5 gardes)
        for i in range(5):
            # Choisir un gardien différent
            caregiver = random.choice([u for u in all_users if u.id != test_user.id])
            plant = random.choice(test_user_plants)

            # Statut aléatoire mais réaliste
            status = random.choice([
                CareStatus.COMPLETED,
                CareStatus.IN_PROGRESS,
                CareStatus.ACCEPTED,
                CareStatus.PENDING
            ])

            # Dates selon le statut
            if status == CareStatus.COMPLETED:
                start_date = datetime.now() - timedelta(days=random.randint(30, 60))
                end_date = start_date + timedelta(days=random.randint(7, 14))
            elif status == CareStatus.IN_PROGRESS:
                start_date = datetime.now() - timedelta(days=random.randint(1, 5))
                end_date = start_date + timedelta(days=random.randint(10, 21))
            elif status == CareStatus.ACCEPTED:
                start_date = datetime.now() + timedelta(days=random.randint(1, 7))
                end_date = start_date + timedelta(days=random.randint(5, 14))
            else:  # PENDING
                start_date = datetime.now() + timedelta(days=random.randint(1, 14))
                end_date = start_date + timedelta(days=random.randint(3, 10))

            lat, lng = get_city_coordinates(test_user.localisation)

            care = PlantCare(
                plant_id=plant.id,
                owner_id=test_user.id,
                caretaker_id=caregiver.id if status != CareStatus.PENDING else None,
                care_instructions=f"Prendre soin de mon {plant.nom} pendant mon voyage",
                start_date=start_date,
                end_date=end_date,
                status=status,
                location=test_user.localisation,
                latitude=lat,
                longitude=lng
            )
            session.add(care)

        # B) Gardes où user@arosaje.fr est gardien (3 gardes)
        for i in range(3):
            # Choisir un propriétaire différent
            owner = random.choice([u for u in all_users if u.id != test_user.id])
            available_plants = [p for p in all_plants if p.owner_id == owner.id]

            if available_plants:
                plant = random.choice(available_plants)

                status = random.choice([CareStatus.ACCEPTED, CareStatus.IN_PROGRESS, CareStatus.COMPLETED])

                if status == CareStatus.COMPLETED:
                    start_date = datetime.now() - timedelta(days=random.randint(20, 45))
                    end_date = start_date + timedelta(days=random.randint(7, 14))
                elif status == CareStatus.IN_PROGRESS:
                    start_date = datetime.now() - timedelta(days=random.randint(1, 3))
                    end_date = start_date + timedelta(days=random.randint(10, 21))
                else:  # ACCEPTED
                    start_date = datetime.now() + timedelta(days=random.randint(1, 5))
                    end_date = start_date + timedelta(days=random.randint(5, 14))

                lat, lng = get_city_coordinates(owner.localisation)

                care = PlantCare(
                    plant_id=plant.id,
                    owner_id=owner.id,
                    caretaker_id=test_user.id,
                    care_instructions=f"Garde acceptée pour {owner.first_name}",
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                    location=owner.localisation,
                    latitude=lat,
                    longitude=lng
                )
                session.add(care)

        # 6. Ajouter des gardes supplémentaires pour atteindre 60 total
        remaining_cares = cares_to_add - 8  # On a déjà ajouté 8 gardes pour user@arosaje.fr

        print(f"Ajout de {remaining_cares} gardes supplementaires...")

        statuts_distribution = [
            CareStatus.COMPLETED,
            CareStatus.COMPLETED,
            CareStatus.COMPLETED,
            CareStatus.IN_PROGRESS,
            CareStatus.IN_PROGRESS,
            CareStatus.ACCEPTED,
            CareStatus.ACCEPTED,
            CareStatus.PENDING,
            CareStatus.CANCELLED,
        ]

        for i in range(remaining_cares):
            # Choisir propriétaire et gardien différents
            owner = random.choice([u for u in all_users if u.role == UserRole.USER])
            caregiver = random.choice([u for u in all_users if u.id != owner.id])
            plant = random.choice([p for p in all_plants if p.owner_id == owner.id] or all_plants)

            status = random.choice(statuts_distribution)

            # Dates selon le statut
            if status == CareStatus.COMPLETED:
                start_date = datetime.now() - timedelta(days=random.randint(30, 90))
                end_date = start_date + timedelta(days=random.randint(3, 14))
            elif status == CareStatus.IN_PROGRESS:
                start_date = datetime.now() - timedelta(days=random.randint(1, 7))
                end_date = start_date + timedelta(days=random.randint(7, 21))
            elif status == CareStatus.ACCEPTED:
                start_date = datetime.now() + timedelta(days=random.randint(1, 7))
                end_date = start_date + timedelta(days=random.randint(5, 14))
            else:  # PENDING, CANCELLED
                start_date = datetime.now() + timedelta(days=random.randint(1, 14))
                end_date = start_date + timedelta(days=random.randint(3, 10))

            lat, lng = get_city_coordinates(owner.localisation)

            care = PlantCare(
                plant_id=plant.id,
                owner_id=owner.id,
                caretaker_id=caregiver.id if status != CareStatus.PENDING else None,
                care_instructions=f"Prendre soin de {plant.nom} pendant une absence",
                start_date=start_date,
                end_date=end_date,
                status=status,
                location=owner.localisation,
                latitude=lat,
                longitude=lng
            )
            session.add(care)

        session.commit()

        # 7. Statistiques finales
        total_cares = session.query(PlantCare).count()
        user_as_owner = session.query(PlantCare).filter(PlantCare.owner_id == test_user.id).count()
        user_as_caregiver = session.query(PlantCare).filter(PlantCare.caretaker_id == test_user.id).count()

        print(f"\nSUCCES:")
        print(f"  Total gardes: {total_cares}")
        print(f"  user@arosaje.fr comme proprietaire: {user_as_owner}")
        print(f"  user@arosaje.fr comme gardien: {user_as_caregiver}")
        print(f"  Application: https://ryan-bouanani.github.io/Arosaje/")
        print(f"  user@arosaje.fr devrait maintenant avoir des gardes dans tous les onglets!")

        return True

    except Exception as e:
        session.rollback()
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = add_test_user_plant_cares()
    sys.exit(0 if success else 1)