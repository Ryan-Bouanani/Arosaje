#!/usr/bin/env python3
"""
CLI avancée pour les seeders A'rosa-je
Interface moderne avec scenarios prédéfinis et options flexibles

Usage:
    python seeders/run.py --help
    python seeders/run.py demo
    python seeders/run.py load --users 50 --plants 20
    python seeders/run.py status
    python seeders/run.py reset --confirm
"""

import argparse
import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from seeders import Statistics
from seeders.user_seeder import UserSeeder
from seeders.plant_seeder import PlantSeeder

class SeedManager:
    """
    Gestionnaire principal des seeders avec scenarios prédéfinis
    """

    SCENARIOS = {
        'demo': {
            'description': 'Données de démo (20 users, 8 plantes, équilibré)',
            'users': 20,
            'botanists': 5,
            'plants': 'all_species',
            'cares': 15,
            'advices': 10,
            'reports': 8
        },
        'dev': {
            'description': 'Environnement de développement (100+ entités)',
            'users': 50,
            'botanists': 10,
            'plants': 30,
            'cares': 40,
            'advices': 25,
            'reports': 20
        },
        'test': {
            'description': 'Tests de performance (500+ entités)',
            'users': 200,
            'botanists': 20,
            'plants': 100,
            'cares': 150,
            'advices': 80,
            'reports': 60
        },
        'minimal': {
            'description': 'Configuration minimale (utilisateurs de base + 8 plantes)',
            'users': 'base_only',
            'plants': 'all_species',
            'cares': 5,
            'advices': 3,
            'reports': 2
        }
    }

    def __init__(self):
        self.start_time = time.time()

    def run_scenario(self, scenario_name):
        """Exécute un scénario prédéfini"""
        if scenario_name not in self.SCENARIOS:
            print(f"ERREUR Scenario inconnu: {scenario_name}")
            print(f"Disponibles: {', '.join(self.SCENARIOS.keys())}")
            return False

        scenario = self.SCENARIOS[scenario_name]
        print(f"Lancement du scenario '{scenario_name}'")
        print(f"   {scenario['description']}\n")

        try:
            self._reset_data()
            self._seed_scenario(scenario)
            self._show_final_stats()
            return True

        except Exception as e:
            print(f"ERREUR pendant le scenario: {e}")
            return False

    def _seed_scenario(self, scenario):
        """Exécute le seeding selon les paramètres du scénario"""

        # 1. Utilisateurs
        with UserSeeder() as user_seeder:
            user_seeder.ensure_base_users()

            if scenario['users'] == 'base_only':
                print("👥 Utilisateurs: comptes de base seulement")
            else:
                users_count = scenario['users']
                botanists_count = scenario.get('botanists', 5)
                regular_count = users_count - botanists_count

                user_seeder.seed_mixed_users(
                    users=regular_count,
                    botanists=botanists_count
                )

        # 2. Plantes
        with PlantSeeder() as plant_seeder:
            if scenario['plants'] == 'all_species':
                plant_seeder.seed_all_species()
            else:
                plant_seeder.seed_realistic_collection(total_plants=scenario['plants'])

            # Vérifier que les 8 images sont utilisées
            plant_seeder.verify_images()

        # 3. Gardes, conseils, rapports (à implémenter)
        print(f"Prevu: {scenario.get('cares', 0)} gardes, {scenario.get('advices', 0)} conseils, {scenario.get('reports', 0)} rapports")

    def _reset_data(self):
        """Reset sécurisé des données"""
        print("Nettoyage des donnees...")

        # Reset dans l'ordre des dépendances (foreign keys)
        # D'abord les plantes, puis les utilisateurs
        with PlantSeeder() as plant_seeder:
            plant_seeder.clear()

        with UserSeeder() as user_seeder:
            user_seeder.clear()

        print("Nettoyage termine\n")

    def _show_final_stats(self):
        """Affiche les statistiques finales"""
        duration = time.time() - self.start_time
        print(f"\nScenario termine en {duration:.2f}s")
        Statistics.show_database_stats()

    def custom_load(self, users=20, botanists=5, plants=10, **kwargs):
        """Chargement personnalisé avec paramètres"""
        print("Chargement personnalise")
        print(f"   Utilisateurs: {users}, Botanistes: {botanists}, Plantes: {plants}\n")

        try:
            self._reset_data()

            # Utilisateurs
            with UserSeeder() as user_seeder:
                user_seeder.ensure_base_users()
                user_seeder.seed_mixed_users(users=users, botanists=botanists)

            # Plantes
            with PlantSeeder() as plant_seeder:
                if plants == 8:
                    plant_seeder.seed_all_species()
                else:
                    plant_seeder.seed_realistic_collection(total_plants=plants)

            self._show_final_stats()
            return True

        except Exception as e:
            print(f"ERREUR: {e}")
            return False

    def reset_confirm(self):
        """Reset avec confirmation"""
        print("ATTENTION: Cette action va supprimer toutes les donnees!")
        print("   (Les comptes de base seront préservés)")

        confirm = input("Tapez 'CONFIRMER' pour continuer: ")
        if confirm == 'CONFIRMER':
            self._reset_data()
            print("Reset termine")
            Statistics.show_database_stats()
        else:
            print("Reset annule")

def create_parser():
    """Crée le parser d'arguments CLI"""
    parser = argparse.ArgumentParser(
        description="Seeders modernisés A'rosa-je avec factory_boy + Faker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
    python seeders/run.py demo                    # Scénario de démo
    python seeders/run.py dev                     # Environnement de dev
    python seeders/run.py load --users 50         # Chargement personnalisé
    python seeders/run.py status                  # Voir les stats
    python seeders/run.py reset --confirm         # Reset complet

Scénarios disponibles:
    demo     - Données de démo (20 users, 8 plantes)
    dev      - Développement (100+ entités)
    test     - Tests performance (500+ entités)
    minimal  - Configuration minimale
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Scénarios prédéfinis
    for scenario in SeedManager.SCENARIOS.keys():
        subparsers.add_parser(scenario, help=f"Scénario {scenario}")

    # Commande load personnalisée
    load_parser = subparsers.add_parser('load', help='Chargement personnalisé')
    load_parser.add_argument('--users', type=int, default=20, help='Nombre d\'utilisateurs')
    load_parser.add_argument('--botanists', type=int, default=5, help='Nombre de botanistes')
    load_parser.add_argument('--plants', type=int, default=10, help='Nombre de plantes')

    # Commande status
    subparsers.add_parser('status', help='Afficher les statistiques')

    # Commande reset
    reset_parser = subparsers.add_parser('reset', help='Reset des données')
    reset_parser.add_argument('--confirm', action='store_true', help='Confirmer le reset')

    return parser

def main():
    """Point d'entrée principal"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = SeedManager()

    # Commandes spéciales
    if args.command == 'status':
        Statistics.show_database_stats()
        return

    if args.command == 'reset':
        if args.confirm:
            manager.reset_confirm()
        else:
            print("ERREUR Utilisez --confirm pour confirmer le reset")
        return

    if args.command == 'load':
        success = manager.custom_load(
            users=args.users,
            botanists=args.botanists,
            plants=args.plants
        )
        sys.exit(0 if success else 1)

    # Scénarios prédéfinis
    if args.command in SeedManager.SCENARIOS:
        success = manager.run_scenario(args.command)
        sys.exit(0 if success else 1)

    # Commande inconnue
    print(f"ERREUR Commande inconnue: {args.command}")
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    main()