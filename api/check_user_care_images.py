#!/usr/bin/env python3
"""
Script pour vérifier et corriger les images des gardes de user@arosaje.fr
"""

import sys
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

from factories.base import SessionLocal
from models.user import User
from models.plant_care import PlantCare
from models.plant import Plant
from factories.plant_factory import PlantFactory

def check_and_fix_user_care_images():
    """Vérifie et corrige les images des gardes de user@arosaje.fr"""
    print("Verification des images des gardes user@arosaje.fr...")
    session = SessionLocal()

    try:
        # 1. Trouver user@arosaje.fr
        test_user = session.query(User).filter(User.email == 'user@arosaje.fr').first()
        if not test_user:
            print("ERREUR: user@arosaje.fr non trouvé")
            return False

        print(f"User trouvé: {test_user.first_name} {test_user.last_name} (ID: {test_user.id})")

        # 2. Vérifier les gardes où user@arosaje.fr est gardien (caretaker)
        cares_as_caretaker = session.query(PlantCare).filter(
            PlantCare.caretaker_id == test_user.id
        ).all()

        print(f"\nGardes comme gardien: {len(cares_as_caretaker)}")

        plants_without_images = []

        for care in cares_as_caretaker:
            plant = care.plant
            print(f"  Garde {care.id}: {plant.nom} (Plante ID: {plant.id})")

            # Vérifier si la plante a une image
            has_image = plant.photo_base64 and plant.photo_base64.strip() != ''
            print(f"    -> Image: {'OUI' if has_image else 'NON'}")

            if not has_image:
                plants_without_images.append(plant)

        # 3. Vérifier les gardes où user@arosaje.fr est propriétaire
        cares_as_owner = session.query(PlantCare).filter(
            PlantCare.owner_id == test_user.id
        ).all()

        print(f"\nGardes comme propriétaire: {len(cares_as_owner)}")

        for care in cares_as_owner:
            plant = care.plant
            print(f"  Garde {care.id}: {plant.nom} (Plante ID: {plant.id})")

            # Vérifier si la plante a une image
            has_image = plant.photo_base64 and plant.photo_base64.strip() != ''
            print(f"    -> Image: {'OUI' if has_image else 'NON'}")

            if not has_image:
                plants_without_images.append(plant)

        # 4. Corriger les plantes sans images
        if plants_without_images:
            print(f"\nCorrection de {len(plants_without_images)} plantes sans images...")

            for plant in plants_without_images:
                print(f"  Correction plante: {plant.nom} (ID: {plant.id})")

                # Essayer d'obtenir l'image correspondante
                plant_image = PlantFactory._get_plant_image(plant.nom)

                if plant_image and plant_image != 'data:image/jpeg;base64,placeholder':
                    plant.photo_base64 = plant_image
                    print(f"    -> Image spécifique ajoutée pour {plant.nom}")
                else:
                    # Utiliser Monstera par défaut
                    default_image = PlantFactory._get_plant_image("Monstera Deliciosa")
                    plant.photo_base64 = default_image
                    print(f"    -> Image par défaut (Monstera) ajoutée pour {plant.nom}")

            # Sauvegarder
            session.commit()
            print(f"\nSUCCES: {len(plants_without_images)} plantes corrigées")
        else:
            print("\nToutes les plantes ont déjà des images !")

        # 5. Vérification finale
        print("\nVérification finale:")

        # Re-vérifier toutes les gardes
        all_user_cares = session.query(PlantCare).filter(
            (PlantCare.caretaker_id == test_user.id) |
            (PlantCare.owner_id == test_user.id)
        ).all()

        plants_still_without_images = 0
        for care in all_user_cares:
            if not care.plant.photo_base64 or care.plant.photo_base64.strip() == '':
                plants_still_without_images += 1

        print(f"  Total gardes user@arosaje.fr: {len(all_user_cares)}")
        print(f"  Plantes encore sans images: {plants_still_without_images}")

        if plants_still_without_images == 0:
            print("  ✅ TOUTES LES GARDES ONT MAINTENANT DES IMAGES !")
        else:
            print(f"  ❌ {plants_still_without_images} plantes nécessitent encore correction")

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
    success = check_and_fix_user_care_images()
    sys.exit(0 if success else 1)