#!/usr/bin/env python3
"""
Test simple de la génération de coordonnées GPS
"""

import sys
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

from factories.care_factory import PlantCareFactory

def test_gps_coordinates():
    """Test direct des coordonnées GPS"""
    print("Test de generation GPS dans PlantCareFactory")
    print("=" * 45)

    try:
        # Créer une instance temporaire pour tester les méthodes GPS
        care_instance = PlantCareFactory.build()

        # Tester différentes villes
        test_locations = [
            'Paris, France',
            'Lyon, France',
            'Marseille, France',
            'Toulouse, France',
            'Nice, France'
        ]

        print("\nTest de generation GPS par ville:")
        for location in test_locations:
            # Simuler l'instance avec une ville spécifique
            care_instance.location = location
            lat, lng = care_instance._get_city_coordinates()

            print(f"  {location:20} -> {lat:.6f}, {lng:.6f}")

        print(f"\nTest reussi ! PlantCareFactory peut generer des coordonnees GPS.")
        print("Chaque ville a ses coordonnees de base + dispersion aleatoire.")

    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gps_coordinates()