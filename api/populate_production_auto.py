#!/usr/bin/env python3
"""
Script automatique de population production avec factory_boy + Faker
Version non-interactive pour les déploiements
"""

import sys
import os
import time
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.append(str(Path(__file__).parent))

from seeders.run import SeedManager

def main():
    """
    Peuple automatiquement la production avec des données factory_boy
    """
    print("🌿 Population Production A'rosa-je avec factory_boy + Faker")
    print("=" * 60)

    manager = SeedManager()

    print("📊 Scénario automatique: 'dev' (100+ entités)")
    print("   - 50 utilisateurs + 10 botanistes")
    print("   - 30 plantes (les 8 espèces + variations)")
    print("   - 40 gardes réalistes")
    print("   - 25 conseils botaniques professionnels")
    print("   - 20 rapports avec images")

    print("\n🚀 Lancement automatique du peuplement...")
    start_time = time.time()

    try:
        # Exécuter le scénario dev automatiquement
        success = manager.run_scenario('dev')

        if success:
            duration = time.time() - start_time
            print(f"\n✅ Population production terminée avec succès !")
            print(f"⏱️  Durée totale: {duration:.2f}s")
            print("\n📋 Comptes de test disponibles:")
            print("   👤 Admin:     root@arosaje.fr     / epsi691")
            print("   🧑 User:      user@arosaje.fr     / epsi691")
            print("   🌿 Botanist:  botanist@arosaje.fr / epsi691")
            print("\n🌐 Production:")
            print("   API:    https://arosaje-backend-t2x7.onrender.com")
            print("   Mobile: https://ryan-bouanani.github.io/Arosaje/")

            # Afficher les statistiques finales
            print("\n📊 Statistiques:")
            from seeders import Statistics
            Statistics.show_database_stats()

        else:
            print("❌ Erreur lors du peuplement production")
            sys.exit(1)

    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()