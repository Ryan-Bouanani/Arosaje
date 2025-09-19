#!/usr/bin/env python3
"""
Test de la génération automatique de coordonnées GPS avec PlantCareFactory
"""

import sys
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

from factories.care_factory import PlantCareFactory
from factories.plant_factory import PlantFactory
from factories.user_factory import UserFactory

def test_gps_generation():
    """Test la génération automatique de coordonnées GPS"""
    print("Test de generation automatique de coordonnees GPS")
    print("=" * 50)

    try:
        # Créer des objets sans sauvegarder en base
        print("Creation de 5 gardes de test...")

        for i in range(5):
            # Créer utilisateur et plante temporaires
            user = UserFactory.build()
            plant = PlantFactory.build(owner=user)

            # Créer garde avec GPS automatique
            care = PlantCareFactory.build(plant=plant, owner=user)

            print(f"\nGarde {i+1}:")
            print(f"  Ville: {care.location}")
            print(f"  GPS: {care.latitude:.6f}, {care.longitude:.6f}")
            print(f"  Statut: {care.status}")
            print(f"  Instructions: {care.care_instructions[:50]}...")

        print(f"\nTest reussi ! Les coordonnees GPS sont generees automatiquement.")
        print("Factory_boy + Faker peut maintenant creer des gardes avec GPS.")

    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gps_generation()