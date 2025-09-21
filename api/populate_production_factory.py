#!/usr/bin/env python3
"""
Script de population production avec factory_boy + Faker
Remplace les anciens scripts par le nouveau système moderne
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
    Peuple la production avec des données factory_boy professionnelles
    """
    print("🌿 Population Production A'rosa-je avec factory_boy + Faker")
    print("=" * 60)

    manager = SeedManager()

    # Scénario dev optimisé pour la production
    print("📊 Scénario sélectionné: 'dev' (100+ entités)")
    print("   - 50 utilisateurs + 10 botanistes")
    print("   - 30 plantes (les 8 espèces + variations)")
    print("   - 40 gardes réalistes")
    print("   - 25 conseils botaniques professionnels")
    print("   - 20 rapports avec images\n")

    # Demander confirmation
    confirm = input("Voulez-vous procéder au peuplement de la production ? (oui/non): ")
    if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return

    print("\n🚀 Lancement du peuplement production...")
    start_time = time.time()

    try:
        # Exécuter le scénario dev
        success = manager.run_scenario('dev')

        if success:
            duration = time.time() - start_time
            print(f"\n✅ Population production terminée avec succès !")
            print(f"⏱️  Durée totale: {duration:.2f}s")
            print("\n📋 Récapitulatif des comptes de test:")
            print("   👤 Admin:     root@arosaje.fr     / epsi691")
            print("   🧑 User:      user@arosaje.fr     / epsi691")
            print("   🌿 Botanist:  botanist@arosaje.fr / epsi691")
            print("\n🌐 API Production: https://arosaje-backend-t2x7.onrender.com")
            print("📱 App Mobile:    https://ryan-bouanani.github.io/Arosaje/")
        else:
            print("❌ Erreur lors du peuplement production")
            sys.exit(1)

    except Exception as e:
        print(f"❌ ERREUR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()