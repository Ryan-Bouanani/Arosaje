"""
UserSeeder - Génération d'utilisateurs français réalistes
"""

from seeders import BaseSeeder
from factories.user_factory import UserFactory, BotanistFactory, RegularUserFactory
from models.user import User, UserRole

class UserSeeder(BaseSeeder):
    """
    Seeder pour générer des utilisateurs français diversifiés

    Utilisation:
        with UserSeeder() as seeder:
            seeder.seed(count=50)
            seeder.seed_botanists(count=10)
            seeder.seed_mixed_users(users=30, botanists=8)
    """

    def seed(self, count=20, **kwargs):
        """
        Génère des utilisateurs standards (85% USER, 15% BOTANIST)

        Args:
            count: Nombre d'utilisateurs à créer
            **kwargs: Arguments passés à UserFactory
        """
        print(f"Création de {count} utilisateurs français...")
        self.start_timer()

        users = UserFactory.create_batch_safe(count, **kwargs)
        self.created_count = len(users)

        self.end_timer()
        return users

    def seed_botanists(self, count=5, **kwargs):
        """
        Génère spécifiquement des botanistes

        Args:
            count: Nombre de botanistes à créer
        """
        print(f"Création de {count} botanistes experts...")
        self.start_timer()

        botanists = BotanistFactory.create_batch_safe(count, **kwargs)
        self.created_count = len(botanists)

        self.end_timer()
        return botanists

    def seed_regular_users(self, count=15, **kwargs):
        """
        Génère spécifiquement des utilisateurs standards

        Args:
            count: Nombre d'utilisateurs à créer
        """
        print(f"Création de {count} utilisateurs standards...")
        self.start_timer()

        users = RegularUserFactory.create_batch_safe(count, **kwargs)
        self.created_count = len(users)

        self.end_timer()
        return users

    def seed_mixed_users(self, users=20, botanists=5, **kwargs):
        """
        Génère un mix d'utilisateurs et botanistes

        Args:
            users: Nombre d'utilisateurs standards
            botanists: Nombre de botanistes
        """
        print(f"Création de {users} utilisateurs + {botanists} botanistes...")
        self.start_timer()

        # Créer les utilisateurs
        regular_users = RegularUserFactory.create_batch_safe(users, **kwargs)
        botanist_users = BotanistFactory.create_batch_safe(botanists, **kwargs)

        self.created_count = len(regular_users) + len(botanist_users)
        self.end_timer()

        return regular_users + botanist_users

    def seed_regional_users(self, regions=None, users_per_region=5):
        """
        Génère des utilisateurs par région

        Args:
            regions: Liste des régions (par défaut: principales villes françaises)
            users_per_region: Nombre d'utilisateurs par région
        """
        if regions is None:
            regions = [
                "Paris, France", "Lyon, France", "Marseille, France",
                "Toulouse, France", "Nice, France", "Nantes, France"
            ]

        print(f"Création d'utilisateurs par région ({len(regions)} régions)...")
        self.start_timer()

        all_users = []
        for region in regions:
            print(f"  Région: {region}")
            users = UserFactory.create_batch_safe(
                users_per_region,
                location=region
            )
            all_users.extend(users)

        self.created_count = len(all_users)
        self.end_timer()

        return all_users

    def ensure_base_users(self):
        """
        S'assure que les utilisateurs de base existent
        (admin, user, botanist avec emails fixes)
        """
        print("Vérification des utilisateurs de base...")

        base_users = [
            {
                'email': 'root@arosaje.fr',
                'role': UserRole.ADMIN,
                'first_name': 'Admin',
                'last_name': 'System'
            },
            {
                'email': 'user@arosaje.fr',
                'role': UserRole.USER,
                'first_name': 'User',
                'last_name': 'Test'
            },
            {
                'email': 'botanist@arosaje.fr',
                'role': UserRole.BOTANIST,
                'first_name': 'Botanist',
                'last_name': 'Expert'
            }
        ]

        created = 0
        for user_data in base_users:
            existing = self.session.query(User).filter(
                User.email == user_data['email']
            ).first()

            if not existing:
                user = UserFactory(**user_data)
                created += 1

        if created > 0:
            print(f"  OK {created} utilisateurs de base créés")
        else:
            print("  OK Utilisateurs de base déjà présents")

    def clear(self):
        """Supprime tous les utilisateurs sauf les comptes de base"""
        print("Suppression des utilisateurs (garde les comptes de base)...")

        self.safe_execute(
            """
            DELETE FROM users WHERE email NOT IN (
                'root@arosaje.fr',
                'user@arosaje.fr',
                'botanist@arosaje.fr'
            )
            """,
            "suppression utilisateurs"
        )

    def clear_all(self):
        """Supprime TOUS les utilisateurs"""
        print("Suppression de TOUS les utilisateurs...")
        self.safe_execute("DELETE FROM users", "suppression totale utilisateurs")

# Export
__all__ = ['UserSeeder']