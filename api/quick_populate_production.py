#!/usr/bin/env python3
"""
Script rapide pour peupler la production avec beaucoup de données
- 50+ utilisateurs français
- 30+ plantes (réutilisation des 8 images)
- 30+ gardes avec différents statuts
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
from factories.user_factory import UserFactory, BotanistFactory, RegularUserFactory
from factories.plant_factory import PlantFactory
from sqlalchemy import text

def create_production_data():
    """Crée rapidement beaucoup de données de test pour la production"""
    print("Creation rapide de donnees de production...")
    session = SessionLocal()

    try:
        # 1. Nettoyer les données existantes (sauf comptes de base)
        print("Nettoyage des donnees existantes...")
        session.query(PlantCare).delete()
        session.query(Plant).delete()
        session.execute(text("""
            DELETE FROM users WHERE email NOT IN (
                'root@arosaje.fr',
                'user@arosaje.fr',
                'botanist@arosaje.fr'
            )
        """))
        session.commit()
        print("  OK Donnees nettoyees")

        # 2. Créer 50 utilisateurs français
        print("Creation de 50 utilisateurs francais...")
        users = RegularUserFactory.create_batch(35)
        botanists = BotanistFactory.create_batch(15)
        all_users = users + botanists
        session.commit()
        print(f"  OK {len(all_users)} utilisateurs crees")

        # 3. Créer 30+ plantes en réutilisant les 8 images
        print("Creation de 35 plantes (reutilisation des 8 especes)...")
        plants = []
        species_names = list(PlantFactory.PLANT_IMAGE_MAPPING.keys())

        # Au moins une de chaque espèce
        for species_name in species_names:
            plant = PlantFactory.create_specific_plant(species_name)
            plants.append(plant)

        # Ajouter des plantes aléatoires pour arriver à 35
        for i in range(35 - len(species_names)):
            species_name = random.choice(species_names)
            plant = PlantFactory.create_specific_plant(species_name)
            plants.append(plant)

        session.commit()
        print(f"  OK {len(plants)} plantes creees")

        # 4. Créer 30+ gardes avec différents statuts
        print("Creation de 35 gardes avec differents statuts...")

        # Statuts réalistes
        statuts_distribution = [
            (CareStatus.COMPLETED, 15),    # 15 gardes terminées
            (CareStatus.IN_PROGRESS, 8),   # 8 gardes en cours
            (CareStatus.ACCEPTED, 6),      # 6 gardes acceptées
            (CareStatus.PENDING, 4),       # 4 gardes en attente
            (CareStatus.CANCELLED, 2),     # 2 gardes annulées
        ]

        cares = []
        for status, count in statuts_distribution:
            for _ in range(count):
                # Choisir un propriétaire et un gardien différents
                owner = random.choice([u for u in all_users if u.role == UserRole.USER])
                caregiver = random.choice([u for u in all_users if u.id != owner.id])
                plant = random.choice(plants)

                # Dates logiques selon le statut
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

                care = PlantCare(
                    plant_id=plant.id,
                    owner_id=owner.id,
                    caregiver_id=caregiver.id if status != CareStatus.PENDING else None,
                    title=f"Garde de {plant.nom}",
                    description=f"Prendre soin de mon {plant.nom} pendant mon absence",
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                    location=owner.localisation
                )
                session.add(care)
                cares.append(care)

        session.commit()
        print(f"  OK {len(cares)} gardes creees")

        # 5. Statistiques finales
        total_users = session.query(User).count()
        total_plants = session.query(Plant).count()
        total_cares = session.query(PlantCare).count()

        print(f"\nPRODUCTION PEUPLEE AVEC SUCCES:")
        print(f"  Utilisateurs: {total_users}")
        print(f"  Plantes: {total_plants}")
        print(f"  Gardes: {total_cares}")
        print(f"  Application: https://ryan-bouanani.github.io/Arosaje/")
        print(f"  API: https://arosaje-backend-t2x7.onrender.com")

        return True

    except Exception as e:
        session.rollback()
        print(f"ERREUR: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = create_production_data()
    sys.exit(0 if success else 1)