#!/usr/bin/env python3
"""
Script pour mettre à jour les plantes avec les vraies images en production
"""

import base64
import os
from sqlalchemy import create_engine, text

# Configuration Neon (production)
DATABASE_URL = "postgresql://neondb_owner:Eh4SSpPaFHhx@ep-spring-bonus-agd7s9t1-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"

def get_image_base64(image_path):
    """Convertit une image en data URL base64"""
    try:
        with open(image_path, 'rb') as f:
            data = f.read()

        # Déterminer l'extension
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = 'image/jpeg' if ext == '.jpg' else 'image/png'

        # Encoder en base64
        b64_data = base64.b64encode(data).decode('utf-8')

        return f'data:{mime_type};base64,{b64_data}'
    except Exception as e:
        print(f"Erreur lors de la conversion de {image_path}: {e}")
        return None

def update_plant_image(engine, plant_id, image_data_url):
    """Met à jour l'image d'une plante"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("UPDATE plants SET photo_base64 = :photo WHERE id = :plant_id"),
                {"photo": image_data_url, "plant_id": plant_id}
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la plante {plant_id}: {e}")
        return False

def main():
    print("Mise a jour des plantes avec les vraies images...")

    # Images locales (à adapter selon vos fichiers)
    images_mapping = {
        24: "C:/Users/ryan4/Downloads/images_plantes/c30fa0f2-f6f5-49ae-831d-db6f2e101156.jpg",  # Monstera de Mamie
        # 25: "C:/Users/ryan4/Downloads/images_plantes/f7250849-a325-4d8f-aff0-6938a440c4ab.jpg",  # Ficus Léon
        # Commençons par juste le Monstera pour tester
    }

    engine = create_engine(DATABASE_URL)

    for plant_id, image_path in images_mapping.items():
        print(f"\nTraitement de la plante ID {plant_id}...")

        if not os.path.exists(image_path):
            print(f"Image non trouvee: {image_path}")
            continue

        # Convertir l'image
        image_data_url = get_image_base64(image_path)
        if not image_data_url:
            continue

        print(f"Image convertie: {len(image_data_url)} caracteres")

        # Mettre à jour en base
        if update_plant_image(engine, plant_id, image_data_url):
            print(f"Plante {plant_id} mise a jour avec succes!")
        else:
            print(f"Echec de la mise a jour de la plante {plant_id}")

    print("\nMise a jour terminee!")

if __name__ == "__main__":
    main()