#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplifie pour seeder la production directement
"""
import os
import sys
from pathlib import Path

# Configuration pour la production
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_ixk4tgXnGJZ9@ep-spring-bonus-agd7s9t1-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require"
os.environ["RENDER"] = "true"

# Ajouter le path
sys.path.append(str(Path(__file__).parent))

def main():
    print("Seed Production A'rosa-je")
    print("=" * 40)

    try:
        from seeders.run import SeedManager
        from seeders import Statistics

        print("Etat initial:")
        Statistics.show_database_stats()

        print("\nLancement dev scenario...")
        manager = SeedManager()
        success = manager.run_scenario('dev')

        if success:
            print("\nProduction seedee !")
            print("\nEtat final:")
            Statistics.show_database_stats()

            print("\nComptes:")
            print("  root@arosaje.fr / epsi691")
            print("  user@arosaje.fr / epsi691")
            print("  botanist@arosaje.fr / epsi691")
        else:
            print("Erreur")

    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()