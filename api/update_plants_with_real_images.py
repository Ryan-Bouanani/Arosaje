#!/usr/bin/env python3
"""
Script pour mettre à jour les plantes en production avec les vraies images base64
Utilise les images renommées dans api/assets/plants/
"""

import sys
import os
import base64
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

# Configuration database
from factories.base import SessionLocal
from models.plant import Plant

# Mapping des images renommées (chemins absolus depuis racine projet)
PLANT_IMAGE_MAPPING = {
    'Monstera Deliciosa': './api/assets/plants/monstera_deliciosa.jpg',
    'Ficus Lyrata': './api/assets/plants/ficus_lyrata.jpg',
    'Sansevieria Trifasciata': './api/assets/plants/sansevieria_trifasciata.jpg',
    'Pothos Doré': './api/assets/plants/pothos_dore.jpg',
    'Zamioculcas Zamiifolia': './api/assets/plants/zamioculcas_zamiifolia.jpg',
    'Chlorophytum Comosum': './api/assets/plants/chlorophytum_comosum.png',
    'Strelitzia Reginae': './api/assets/plants/strelitzia_reginae.png',
    'Dracaena Marginata': './api/assets/plants/dracaena_marginata.jpg'
}

def image_to_base64(image_path):
    """Convertit une image en data URL base64"""
    try:
        with open(image_path, 'rb') as f:
            data = f.read()

        ext = os.path.splitext(image_path)[1].lower()
        mime_type = 'image/jpeg' if ext == '.jpg' else 'image/png'
        b64_data = base64.b64encode(data).decode('utf-8')
        return f'data:{mime_type};base64,{b64_data}'
    except Exception as e:
        print(f'Erreur conversion image {image_path}: {e}')
        return None

def update_plants_with_images():
    """Met à jour toutes les plantes avec leurs vraies images"""
    print("Mise a jour des plantes avec les vraies images...")

    session = SessionLocal()
    updated_count = 0

    try:
        # Récupérer toutes les plantes
        plants = session.query(Plant).all()
        print(f"Trouvé {len(plants)} plantes en base")

        for plant in plants:
            if plant.nom in PLANT_IMAGE_MAPPING:
                image_path = PLANT_IMAGE_MAPPING[plant.nom]
                print(f"Traitement de {plant.nom}...")

                # Convertir l'image en base64
                base64_image = image_to_base64(image_path)

                if base64_image:
                    plant.photo_base64 = base64_image
                    updated_count += 1
                    print(f"  OK Image mise a jour pour {plant.nom}")
                else:
                    print(f"  ERREUR Image non trouvee pour {plant.nom}")
            else:
                print(f"  SKIP Pas de mapping pour {plant.nom}")

        # Sauvegarder les changements
        session.commit()
        print(f"\nSUCCES: {updated_count} plantes mises a jour avec leurs vraies images")

    except Exception as e:
        session.rollback()
        print(f"ERREUR: {e}")
    finally:
        session.close()

def main():
    """Point d'entrée principal"""
    print("Script de mise a jour des images de plantes")
    print("=========================================\n")

    # Vérifier que les images existent
    missing_images = []
    for plant_name, image_path in PLANT_IMAGE_MAPPING.items():
        if not os.path.exists(image_path):
            missing_images.append(f"{plant_name}: {image_path}")

    if missing_images:
        print("ERREUR: Images manquantes:")
        for missing in missing_images:
            print(f"  - {missing}")
        return

    print("Toutes les images sont presentes, mise a jour en cours...\n")
    update_plants_with_images()

if __name__ == "__main__":
    main()