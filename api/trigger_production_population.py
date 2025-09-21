#!/usr/bin/env python3
"""
Script pour déclencher la population de la production via HTTP
"""
import requests
import json
import time

def trigger_population():
    """Déclenche la population via l'API de production"""

    url = "https://arosaje-backend-t2x7.onrender.com"

    print("Declenchement de la population production via API")
    print("=" * 55)

    try:
        # Vérifier que l'API est accessible
        print("Verification de l'API...")
        health_response = requests.get(f"{url}/health", timeout=30)
        if health_response.status_code == 200:
            print("API accessible")
        else:
            print(f"API non accessible: {health_response.status_code}")
            return False

        # Essayer de déclencher via un endpoint si disponible
        print("\nTentative de population via endpoint...")

        # Créer un payload pour déclencher la population
        payload = {
            "action": "populate",
            "scenario": "dev",
            "force": True
        }

        # Essayer plusieurs endpoints possibles
        endpoints = [
            "/admin/populate-production",
            "/admin/populate",
            "/populate",
            "/seed"
        ]

        for endpoint in endpoints:
            try:
                print(f"   Essai: {endpoint}")
                response = requests.post(f"{url}{endpoint}", json=payload, timeout=300)

                if response.status_code == 200:
                    print(f"Population declenchee via {endpoint}")
                    result = response.json()
                    print(f"Resultat: {json.dumps(result, indent=2)}")
                    return True
                elif response.status_code == 404:
                    print(f"   Endpoint {endpoint} non trouve")
                else:
                    print(f"   Erreur {response.status_code}: {response.text}")

            except requests.RequestException as e:
                print(f"   Erreur de requete: {e}")

        print("Aucun endpoint de population trouve")
        return False

    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = trigger_population()
    if not success:
        print("\nAlternative: Utiliser le script SSH ou le deploiement local")
        print("   1. docker exec arosa-je-api python populate_production_auto.py")
        print("   2. Puis pousser les données vers Render")