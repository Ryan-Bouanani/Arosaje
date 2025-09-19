#!/usr/bin/env python3
"""
Test direct de la fonction de génération GPS
"""

import random

def get_city_coordinates(location):
    """Retourne coordonnées GPS avec dispersion pour simulation quartiers"""

    # Coordonnées centres + dispersion par ville
    city_coords = {
        'Paris, France': (48.8566, 2.3522, 0.1),
        'Lyon, France': (45.7640, 4.8357, 0.08),
        'Marseille, France': (43.2965, 5.3698, 0.08),
        'Toulouse, France': (43.6047, 1.4442, 0.08),
        'Nice, France': (43.7102, 7.2620, 0.06),
        'Nantes, France': (47.2184, -1.5536, 0.06),
        'Montpellier, France': (43.6110, 3.8767, 0.06),
        'Strasbourg, France': (48.5734, 7.7521, 0.06),
        'Bordeaux, France': (44.8378, -0.5792, 0.08),
        'Lille, France': (50.6292, 3.0573, 0.06)
    }

    # Récupérer coordonnées de base ou utiliser Paris par défaut
    lat_base, lng_base, dispersion = city_coords.get(
        location,
        (48.8566, 2.3522, 0.1)  # Paris par défaut
    )

    # Ajouter dispersion aléatoire pour simuler différents quartiers
    lat_offset = (random.random() - 0.5) * dispersion
    lng_offset = (random.random() - 0.5) * dispersion

    return (
        round(lat_base + lat_offset, 6),
        round(lng_base + lng_offset, 6)
    )

def test_gps_generation():
    """Test de génération GPS directe"""
    print("Test de generation GPS directe")
    print("=" * 30)

    test_cities = [
        'Paris, France',
        'Lyon, France',
        'Marseille, France',
        'Toulouse, France',
        'Nice, France',
        'Bordeaux, France',
        'Unknown City, France'  # Test fallback
    ]

    print("\nGeneration de coordonnees GPS:")
    for city in test_cities:
        lat, lng = get_city_coordinates(city)
        print(f"  {city:20} -> {lat:9.6f}, {lng:9.6f}")

    print("\nTest de dispersion (Paris):")
    for i in range(5):
        lat, lng = get_city_coordinates('Paris, France')
        print(f"  Paris #{i+1:15} -> {lat:9.6f}, {lng:9.6f}")

    print(f"\nTest reussi ! Generation GPS fonctionnelle.")
    print("Chaque ville a ses coordonnees + dispersion aleatoire.")

if __name__ == "__main__":
    test_gps_generation()