"""
PlantSeeder - Génération de plantes avec vraies images
"""

from seeders import BaseSeeder
from factories.plant_factory import (
    PlantFactory, MonsteraFactory, FicusFactory, SansevieriaFactory,
    PothosFactory, ZamioculcasFactory, ChlorophytumFactory,
    StrelitziaFactory, DracaenaFactory
)
from models.plant import Plant
from models.user import User, UserRole

class PlantSeeder(BaseSeeder):
    """
    Seeder pour générer des plantes avec les 8 vraies images

    Utilisation:
        with PlantSeeder() as seeder:
            seeder.seed_all_species()      # Les 8 vraies images
            seeder.seed(count=20)          # 20 plantes aléatoires
            seeder.seed_collection()       # Collection réaliste
    """

    def seed(self, count=10, **kwargs):
        """
        Génère des plantes aléatoires parmi les 8 espèces

        Args:
            count: Nombre de plantes à créer
            **kwargs: Arguments passés à PlantFactory
        """
        print(f"Création de {count} plantes aléatoires...")
        self.start_timer()

        plants = PlantFactory.create_batch_safe(count, **kwargs)
        self.created_count = len(plants)

        self.end_timer()
        return plants

    def seed_all_species(self, **kwargs):
        """
        Crée une plante de chaque espèce (garantit les 8 vraies images)

        Returns:
            Liste des 8 plantes créées
        """
        print("Création des 8 espèces avec vraies images...")
        self.start_timer()

        plants = PlantFactory.create_all_species(**kwargs)
        self.created_count = len(plants)

        print("  Espèces créées:")
        for plant in plants:
            print(f"    • {plant.nom}")

        self.end_timer()
        return plants

    def seed_specific_collections(self):
        """
        Crée des collections spécialisées pour différents types d'utilisateurs
        """
        print("Création de collections spécialisées...")
        self.start_timer()

        all_plants = []

        # Collection débutant (plantes faciles)
        print("  Collection débutant (plantes résistantes):")
        beginner_plants = [
            SansevieriaFactory(),  # Très résistante
            ZamioculcasFactory(),  # Tolère la négligence
            ChlorophytumFactory()  # Facile à multiplier
        ]
        all_plants.extend(beginner_plants)

        # Collection expert (plantes exigeantes)
        print("  Collection expert (plantes délicates):")
        expert_plants = [
            FicusFactory(),        # Sensible aux changements
            StrelitziaFactory(),   # Besoin d'humidité
            MonsteraFactory()      # Croissance complexe
        ]
        all_plants.extend(expert_plants)

        # Collection décorative
        print("  Collection décorative:")
        decorative_plants = [
            PothosFactory(),       # Suspension
            DracaenaFactory()      # Port élégant
        ]
        all_plants.extend(decorative_plants)

        self.created_count = len(all_plants)
        self.end_timer()

        return all_plants

    def seed_by_owners(self, users_per_plant=2):
        """
        Distribue les plantes entre différents propriétaires

        Args:
            users_per_plant: Nombre moyen de plantes par utilisateur
        """
        # Récupérer les utilisateurs disponibles
        owners = self.session.query(User).filter(
            User.role.in_([UserRole.USER, UserRole.BOTANIST])
        ).all()

        if not owners:
            print("  ATTENTION Aucun propriétaire disponible, création d'utilisateurs...")
            from seeders.user_seeder import UserSeeder
            with UserSeeder() as user_seeder:
                owners = user_seeder.seed_mixed_users(users=10, botanists=3)

        print(f"Distribution des plantes entre {len(owners)} propriétaires...")
        self.start_timer()

        all_plants = []

        for owner in owners:
            # Chaque propriétaire a 1-4 plantes
            plant_count = min(users_per_plant, 4)
            plants = PlantFactory.create_batch_safe(plant_count, owner=owner)
            all_plants.extend(plants)

            print(f"  {owner.first_name} {owner.last_name}: {len(plants)} plantes")

        self.created_count = len(all_plants)
        self.end_timer()

        return all_plants

    def seed_realistic_collection(self, total_plants=30):
        """
        Crée une collection réaliste avec distribution équilibrée

        Args:
            total_plants: Nombre total de plantes à créer
        """
        print(f"Création d'une collection réaliste de {total_plants} plantes...")
        self.start_timer()

        all_plants = []

        # Garantir au moins une de chaque espèce (8 plantes)
        core_plants = PlantFactory.create_all_species()
        all_plants.extend(core_plants)
        remaining = total_plants - 8

        if remaining > 0:
            # Distribuer le reste avec préférence pour les plantes populaires
            popular_factories = [
                MonsteraFactory,      # Très populaire
                PothosFactory,        # Facile d'entretien
                SansevieriaFactory,   # Résistante
                FicusFactory          # Décorative
            ]

            for i in range(remaining):
                factory = popular_factories[i % len(popular_factories)]
                plant = factory()
                all_plants.append(plant)

        self.created_count = len(all_plants)

        # Statistiques de distribution
        distribution = {}
        for plant in all_plants:
            species = plant.nom
            distribution[species] = distribution.get(species, 0) + 1

        print("  Distribution par espèce:")
        for species, count in distribution.items():
            print(f"    • {species}: {count}")

        self.end_timer()
        return all_plants

    def clear(self):
        """Supprime toutes les plantes"""
        print("Suppression de toutes les plantes...")
        self.safe_execute("DELETE FROM plants", "suppression plantes")

    def verify_images(self):
        """Vérifie que toutes les vraies images sont utilisées"""
        print("Vérification des images utilisées...")

        plants = self.session.query(Plant).all()
        used_species = set(plant.nom for plant in plants)
        all_species = set(PlantFactory.PLANT_IMAGE_MAPPING.keys())

        missing = all_species - used_species
        if missing:
            print(f"  ATTENTION Espèces manquantes: {', '.join(missing)}")
            return False
        else:
            print(f"  OK Toutes les {len(all_species)} espèces sont présentes")
            return True

# Export
__all__ = ['PlantSeeder']