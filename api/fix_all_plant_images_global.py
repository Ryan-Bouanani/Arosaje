#!/usr/bin/env python3
"""
Script pour corriger TOUTES les plantes sans images dans la base
"""

import sys
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

from factories.base import SessionLocal
from models.plant import Plant
from factories.plant_factory import PlantFactory

def fix_all_plant_images_global():
    """Corrige toutes les plantes sans images dans la base globalement"""
    print("Correction globale de toutes les plantes sans images...")
    session = SessionLocal()

    try:
        # 1. Compter toutes les plantes
        total_plants = session.query(Plant).count()
        print(f"Total plantes en base: {total_plants}")

        # 2. Trouver plantes sans images
        plants_without_images = session.query(Plant).filter(
            (Plant.photo_base64 == None) |
            (Plant.photo_base64 == '') |
            (Plant.photo_base64 == 'data:image/jpeg;base64,placeholder')
        ).all()

        print(f"Plantes sans images: {len(plants_without_images)}")

        if len(plants_without_images) == 0:
            print("Toutes les plantes ont deja des images!")
            return True

        # 3. Corriger chaque plante
        fixed_count = 0
        for plant in plants_without_images:
            print(f"Correction: {plant.nom} (ID: {plant.id})")

            # Essayer l'image spécifique
            plant_image = PlantFactory._get_plant_image(plant.nom)

            if plant_image and plant_image != 'data:image/jpeg;base64,placeholder':
                plant.photo_base64 = plant_image
                print(f"  -> Image specifique ajoutee")
            else:
                # Image par défaut Monstera
                default_image = PlantFactory._get_plant_image("Monstera Deliciosa")
                plant.photo_base64 = default_image
                print(f"  -> Image par defaut ajoutee")

            fixed_count += 1

        # 4. Sauvegarder
        session.commit()
        print(f"\nSUCCES: {fixed_count} plantes corrigees")

        # 5. Vérification finale
        remaining_without_images = session.query(Plant).filter(
            (Plant.photo_base64 == None) |
            (Plant.photo_base64 == '') |
            (Plant.photo_base64 == 'data:image/jpeg;base64,placeholder')
        ).count()

        print(f"Plantes encore sans images: {remaining_without_images}")

        if remaining_without_images == 0:
            print("TOUTES LES PLANTES ONT MAINTENANT DES IMAGES!")

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
    success = fix_all_plant_images_global()
    sys.exit(0 if success else 1)