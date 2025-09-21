#!/usr/bin/env python3
"""
Script d'initialisation automatique pour la production
Détecte si on est en production et peuple automatiquement
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.append(str(Path(__file__).parent))

def is_production():
    """Détecte si on est en environnement de production"""
    # Variables d'environnement Render
    return (
        os.getenv('RENDER') == 'true' or
        os.getenv('RENDER_SERVICE_ID') is not None or
        'render.com' in os.getenv('DATABASE_URL', '')
    )

def main():
    """Point d'entrée principal"""

    if not is_production():
        print("❌ Ce script est réservé à la production")
        return

    print("🌿 Initialisation automatique de la production Render")
    print("=" * 55)

    try:
        # Importer les modules après avoir configuré le path
        from seeders.run import SeedManager
        from seeders import Statistics

        # Vérifier l'état actuel
        print("📊 État actuel de la base de données:")
        Statistics.show_database_stats()

        manager = SeedManager()

        # Exécuter le scénario dev automatiquement
        print("\n🚀 Lancement du scénario 'dev' pour la production...")
        success = manager.run_scenario('dev')

        if success:
            print("\n✅ Production initialisée avec succès !")
            print("\n📊 État final:")
            Statistics.show_database_stats()

            print("\n📋 Comptes disponibles:")
            print("   👤 Admin:     root@arosaje.fr     / epsi691")
            print("   🧑 User:      user@arosaje.fr     / epsi691")
            print("   🌿 Botanist:  botanist@arosaje.fr / epsi691")
        else:
            print("\n❌ Erreur lors de l'initialisation")

    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()