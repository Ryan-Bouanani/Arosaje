#!/usr/bin/env python3
"""
Script pour exécuter les seeders factory_boy + Faker directement en production
Utilise la base Neon PostgreSQL et génère des données françaises réalistes
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.append(str(Path(__file__).parent))

from seeders.run import SeedManager

def main():
    """Exécute le scénario demo en production"""
    print("Execution des seeders factory_boy + Faker en PRODUCTION")
    print("Base: Neon PostgreSQL")
    print("Donnees: Francaises realistes via Faker\n")

    try:
        manager = SeedManager()
        success = manager.run_scenario('demo')

        if success:
            print("\nSeeders factory_boy executes avec succes en production !")
            print("Scenario demo: 20 users + 8 plantes + gardes/conseils")
            print("Application prete: https://ryan-bouanani.github.io/Arosaje/")
        else:
            print("\nErreur lors de l'execution des seeders")
            sys.exit(1)

    except Exception as e:
        print(f"\nERREUR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()