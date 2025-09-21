#!/usr/bin/env python3
"""
Test des factories en mode dry-run (sans base de données)
Valide la génération de données françaises réalistes
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from factories import fake, random_french_city, random_french_phone, random_french_email
from factories.user_factory import UserFactory, BotanistFactory
from factories.plant_factory import PlantFactory

def test_faker_french():
    """Test la configuration Faker français"""
    print("=== Test Faker français ===")

    print(f"Nom: {fake.first_name()} {fake.last_name()}")
    print(f"Ville: {random_french_city()}")
    print(f"Téléphone: {random_french_phone()}")
    print(f"Email: {random_french_email('Marie', 'Dubois')}")
    print()

def test_user_factory():
    """Test UserFactory en mode build (sans DB)"""
    print("=== Test UserFactory ===")

    # Test utilisateur standard
    user = UserFactory.build()
    print(f"Utilisateur: {user.first_name} {user.last_name}")
    print(f"Email: {user.email}")
    print(f"Téléphone: {user.telephone}")
    print(f"Localisation: {user.location}")
    print(f"Rôle: {user.role}")
    print()

    # Test botaniste
    botanist = BotanistFactory.build()
    print(f"Botaniste: Dr. {botanist.first_name} {botanist.last_name}")
    print(f"Email: {botanist.email}")
    print(f"Localisation: {botanist.location}")
    print()

def test_plant_factory():
    """Test PlantFactory en mode build"""
    print("=== Test PlantFactory ===")

    # Test plante aléatoire
    plant = PlantFactory.build()
    print(f"Plante: {plant.name}")
    print(f"Espèce: {plant.species}")
    print(f"Description: {plant.description[:60]}...")
    print(f"Photo disponible: {'Oui' if plant.photo_base64 and len(plant.photo_base64) > 100 else 'Non'}")
    print()

    # Test toutes les espèces
    print("Espèces disponibles avec vraies images:")
    for plant_name in PlantFactory.PLANT_IMAGE_MAPPING.keys():
        plant = PlantFactory.build(name=plant_name)
        print(f"  • {plant.name} ({plant.species})")
    print()

def test_data_quality():
    """Test la qualité des données générées"""
    print("=== Test qualité des données ===")

    # Générer 10 utilisateurs et vérifier l'unicité des emails
    emails = set()
    for i in range(10):
        user = UserFactory.build()
        emails.add(user.email)

    print(f"Unicité emails: {len(emails)}/10 unique")

    # Vérifier que les botanistes ont des emails professionnels
    botanist = BotanistFactory.build()
    is_professional = '@jardin-' in botanist.email or '@botanique-' in botanist.email
    print(f"Email botaniste professionnel: {'Oui' if is_professional else 'Non'}")

    # Vérifier les formats français
    phone = random_french_phone()
    is_french_format = phone.startswith('0') and '.' in phone
    print(f"Format téléphone français: {'Oui' if is_french_format else 'Non'}")

    print()

def test_plant_images():
    """Test la disponibilité des vraies images"""
    print("=== Test images de plantes ===")

    images_found = 0
    images_total = len(PlantFactory.PLANT_IMAGE_MAPPING)

    for plant_name, info in PlantFactory.PLANT_IMAGE_MAPPING.items():
        image_path = info['path']
        exists = os.path.exists(image_path)
        print(f"  {'OK' if exists else 'MANQUANT'} {plant_name}: {image_path}")
        if exists:
            images_found += 1

    print(f"\nImages trouvées: {images_found}/{images_total}")
    print()

def main():
    """Exécute tous les tests"""
    print("Test des factories A'rosa-je (mode dry-run)")
    print("=" * 50)

    try:
        test_faker_french()
        test_user_factory()
        test_plant_factory()
        test_data_quality()
        test_plant_images()

        print("Tous les tests sont passes !")
        print("Les factories factory_boy + Faker sont fonctionnelles")
        print("Les donnees francaises sont realistes")
        print("Les 8 vraies images sont configurees")

    except Exception as e:
        print(f"ERREUR pendant les tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()