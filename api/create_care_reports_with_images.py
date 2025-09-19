#!/usr/bin/env python3
"""
Script pour créer des rapports de séance avec images pour les gardes actives
Génère des rapports réalistes avec photos avant/après
"""

import sys
import os
from pathlib import Path
import random
from datetime import datetime, timedelta

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

from factories.base import SessionLocal
from models.plant_care import PlantCare, CareStatus
from models.care_report import CareReport, HealthLevel
from models.user import User
from factories.plant_factory import PlantFactory

def create_care_reports_with_images():
    """Crée des rapports de séance avec images pour les gardes en cours/terminées"""
    print("Creation de rapports de seance avec images...")
    session = SessionLocal()

    try:
        # 1. Trouver les gardes qui peuvent avoir des rapports
        eligible_cares = session.query(PlantCare).filter(
            PlantCare.status.in_([CareStatus.IN_PROGRESS, CareStatus.COMPLETED])
        ).all()

        print(f"Gardes eligibles pour rapports: {len(eligible_cares)}")

        # 2. Vérifier combien ont déjà des rapports
        existing_reports = session.query(CareReport).count()
        print(f"Rapports existants: {existing_reports}")

        reports_created = 0

        # 3. Créer des rapports pour 60% des gardes éligibles
        for care in eligible_cares:
            # Skip si déjà des rapports pour cette garde
            existing_for_care = session.query(CareReport).filter(
                CareReport.plant_care_id == care.id
            ).count()

            if existing_for_care > 0:
                continue  # Déjà des rapports

            # 60% de chance de créer un rapport
            if random.random() < 0.6:
                # Date du rapport pendant la période de garde
                if care.status == CareStatus.COMPLETED:
                    # Rapport pendant la garde (passée)
                    report_date = care.start_date + timedelta(
                        days=random.randint(1, (care.end_date - care.start_date).days)
                    )
                else:  # IN_PROGRESS
                    # Rapport récent
                    days_since_start = (datetime.now() - care.start_date).days
                    if days_since_start > 0:
                        report_date = care.start_date + timedelta(
                            days=random.randint(1, min(days_since_start, 7))
                        )
                    else:
                        report_date = datetime.now()

                # Récupérer une image de plante pour le rapport
                plant_image = None
                if care.plant and care.plant.nom:
                    plant_image = PlantFactory._get_plant_image(care.plant.nom)

                if not plant_image or plant_image == 'data:image/jpeg;base64,placeholder':
                    # Image par défaut
                    default_plants = list(PlantFactory.PLANT_IMAGE_MAPPING.keys())
                    plant_image = PlantFactory._get_plant_image(default_plants[0])

                # Niveaux de santé réalistes
                health_levels = [HealthLevel.BAS, HealthLevel.MOYEN, HealthLevel.BON]
                health_weights = [0.1, 0.3, 0.6]  # Plus souvent "BON"

                health = random.choices(health_levels, weights=health_weights)[0]
                hydration = random.choices(health_levels, weights=health_weights)[0]
                vitality = random.choices(health_levels, weights=health_weights)[0]

                # Description contextuelle
                descriptions = [
                    f"Arrosage effectué pour {care.plant.nom}. La plante semble en bonne santé.",
                    f"Vérification quotidienne de {care.plant.nom}. Feuillage en bon état.",
                    f"Nettoyage des feuilles de {care.plant.nom} et rotation pour exposition lumière.",
                    f"Surveillance attentive de {care.plant.nom}. Aucun problème détecté.",
                    f"Entretien de {care.plant.nom} selon les instructions du propriétaire.",
                    f"Inspection de {care.plant.nom}. Croissance normale observée."
                ]

                description = random.choice(descriptions)

                # Créer le rapport
                report = CareReport(
                    plant_care_id=care.id,
                    caretaker_id=care.caretaker_id,
                    session_date=report_date,
                    photo_base64=plant_image,
                    health_level=health,
                    hydration_level=hydration,
                    vitality_level=vitality,
                    description=description,
                    created_at=report_date
                )

                session.add(report)
                reports_created += 1

                print(f"  Rapport cree pour garde {care.id} ({care.plant.nom})")

        # 4. Sauvegarder
        session.commit()

        # 5. Statistiques finales
        total_reports = session.query(CareReport).count()

        print(f"\nSUCCES:")
        print(f"  Nouveaux rapports crees: {reports_created}")
        print(f"  Total rapports: {total_reports}")
        print(f"  Gardes avec rapports: {len(set(r.plant_care_id for r in session.query(CareReport).all()))}")
        print(f"  Tous les rapports ont maintenant des images base64!")

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
    success = create_care_reports_with_images()
    sys.exit(0 if success else 1)