#!/usr/bin/env python3
"""
Script rapide pour corriger toutes les images manquantes
"""

import sys
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

from factories.base import SessionLocal
from models.plant import Plant
from models.care_report import CareReport
from factories.plant_factory import PlantFactory

def quick_fix_all_images():
    """Correction rapide de toutes les images manquantes"""
    print("Correction rapide de toutes les images...")
    session = SessionLocal()

    try:
        # 1. Corriger les plantes sans images
        plants_without_images = session.query(Plant).filter(
            (Plant.photo_base64 == None) | (Plant.photo_base64 == '')
        ).all()

        print(f"Plantes a corriger: {len(plants_without_images)}")

        # Image par défaut (Monstera)
        default_image = PlantFactory._get_plant_image("Monstera Deliciosa")

        for plant in plants_without_images:
            plant.photo_base64 = default_image

        # 2. Corriger les rapports sans images
        reports_without_images = session.query(CareReport).filter(
            (CareReport.photo_base64 == None) | (CareReport.photo_base64 == '')
        ).all()

        print(f"Rapports a corriger: {len(reports_without_images)}")

        for report in reports_without_images:
            report.photo_base64 = default_image

        # 3. Sauvegarder
        session.commit()

        print(f"SUCCES: {len(plants_without_images)} plantes + {len(reports_without_images)} rapports corriges")

        return True

    except Exception as e:
        session.rollback()
        print(f"ERREUR: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = quick_fix_all_images()
    sys.exit(0 if success else 1)