#!/usr/bin/env python3
import base64
import os

def image_to_base64(image_path):
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
        print(f'Erreur conversion image {image_path}: {e}')
        return None

# Mapping des 8 images vers les plantes
images_mapping = {
    'api/assets/plants/c30fa0f2-f6f5-49ae-831d-db6f2e101156.jpg': 'Monstera Deliciosa',
    'api/assets/plants/f7250849-a325-4d8f-aff0-6938a440c4ab.jpg': 'Ficus Lyrata',
    'api/assets/plants/fe70ee54-62c7-49ff-a1cc-ed1cbf7b0092.jpg': 'Sansevieria Trifasciata',
    'api/assets/plants/b928e83d-d68e-4be2-af5d-53a37c589f92.jpg': 'Pothos Doré',
    'api/assets/plants/3ec6b4c8-f0bd-44e5-929e-3000b28e891c.jpg': 'Zamioculcas Zamiifolia',
    'api/assets/plants/11471877.png': 'Chlorophytum Comosum',
    'api/assets/plants/11471878.png': 'Strelitzia Reginae',
    'api/assets/plants/plante-de-palmier-en-pot.jpg': 'Dracaena Marginata'
}

print("Conversion des 8 images en base64...")
for image_path, plant_name in images_mapping.items():
    if os.path.exists(image_path):
        base64_data = image_to_base64(image_path)
        if base64_data:
            print(f"OK {plant_name}: {len(base64_data)} caracteres")
            # Sauvegarder dans un fichier pour chaque plante
            filename = f"plant_{plant_name.replace(' ', '_').lower()}.txt"
            with open(filename, 'w') as f:
                f.write(base64_data)
        else:
            print(f"ERREUR avec {plant_name}")
    else:
        print(f"ERREUR Image manquante: {image_path}")

print("Conversion terminee!")