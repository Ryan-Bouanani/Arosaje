#!/usr/bin/env python3
"""
Script pour corriger les plantes sans images base64
Utilise les vraies images des factories pour compléter
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

from factories.base import SessionLocal
from models.plant import Plant
from factories.plant_factory import PlantFactory

def fix_missing_plant_images():
    """Corrige toutes les plantes qui n'ont pas d'images base64"""
    print("Correction des images manquantes pour les plantes...")
    session = SessionLocal()

    try:
        # 1. Trouver toutes les plantes sans image
        plants_without_images = session.query(Plant).filter(
            (Plant.photo_base64 == None) | (Plant.photo_base64 == '')
        ).all()

        print(f"Plantes sans images trouvees: {len(plants_without_images)}")

        if not plants_without_images:
            print("Toutes les plantes ont deja des images !")
            return True

        # 2. Corriger chaque plante
        fixed_count = 0
        for plant in plants_without_images:
            print(f"Correction plante: {plant.nom} (ID: {plant.id})")

            # Trouver l'image correspondante
            plant_image = PlantFactory._get_plant_image(plant.nom)

            if plant_image and plant_image != 'data:image/jpeg;base64,placeholder':
                plant.photo_base64 = plant_image
                fixed_count += 1
                print(f"  -> Image ajoutee pour {plant.nom}")
            else:
                # Utiliser une image par défaut si le nom ne correspond pas
                default_plants = list(PlantFactory.PLANT_IMAGE_MAPPING.keys())
                default_plant = default_plants[0]  # Monstera par défaut
                plant.photo_base64 = PlantFactory._get_plant_image(default_plant)
                fixed_count += 1
                print(f"  -> Image par defaut (Monstera) ajoutee pour {plant.nom}")

        # 3. Sauvegarder
        session.commit()
        print(f"\nSUCCES: {fixed_count} plantes corrigees")

        # 4. Vérification finale
        remaining_without_images = session.query(Plant).filter(
            (Plant.photo_base64 == None) | (Plant.photo_base64 == '')
        ).count()

        print(f"Plantes encore sans images: {remaining_without_images}")

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
    success = fix_missing_plant_images()
    sys.exit(0 if success else 1)