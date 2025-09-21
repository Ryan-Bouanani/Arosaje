"""
PlantFactory - Génération de plantes avec vraies images
Utilise les 8 vraies images fournies et des données botaniques réalistes
"""

import factory
import random
import os
from factories.base import BaseFactory, ImageMixin
from factories import fake, random_plant_name
from models.plant import Plant
from models.user import User, UserRole

class PlantFactory(BaseFactory, ImageMixin):
    """
    Factory pour générer des plantes avec les vraies images fournies

    Exemples:
        # Plante avec image aléatoire
        plant = PlantFactory()

        # Plante spécifique
        monstera = PlantFactory(name="Monstera Deliciosa")

        # Lot de plantes
        plants = PlantFactory.create_batch(8)  # Une pour chaque image

        # Plante pour un propriétaire spécifique
        my_plant = PlantFactory(owner=my_user)
    """

    class Meta:
        model = Plant
        exclude = ['PLANT_IMAGE_MAPPING']

    # Mapping des 8 vraies images vers les plantes (chemins mis à jour)
    PLANT_IMAGE_MAPPING = {
        'Monstera Deliciosa': {
            'path': 'assets/plants/monstera_deliciosa.jpg',
            'species': 'Monstera deliciosa',
            'description': 'Une magnifique plante tropicale aux feuilles perforées, parfaite pour décorer votre intérieur. Ses grandes feuilles sculptées en font une star de la décoration végétale.'
        },
        'Ficus Lyrata': {
            'path': 'assets/plants/ficus_lyrata.jpg',
            'species': 'Ficus lyrata',
            'description': 'Le figuier lyre, une plante élégante avec de grandes feuilles en forme de violon. Très appréciée pour son port majestueux et ses feuilles brillantes.'
        },
        'Sansevieria Trifasciata': {
            'path': 'assets/plants/sansevieria_trifasciata.jpg',
            'species': 'Sansevieria trifasciata',
            'description': 'La langue de belle-mère, une plante résistante et purificatrice d\'air. Parfaite pour les débutants grâce à sa grande tolérance.'
        },
        'Pothos Doré': {
            'path': 'assets/plants/pothos_dore.jpg',
            'species': 'Epipremnum aureum',
            'description': 'Une plante grimpante facile à entretenir, parfaite pour les suspensions. Ses feuilles dorées apportent de la lumière à votre intérieur.'
        },
        'Zamioculcas Zamiifolia': {
            'path': 'assets/plants/zamioculcas_zamiifolia.jpg',
            'species': 'Zamioculcas zamiifolia',
            'description': 'La plante ZZ, robuste et brillante, idéale pour les espaces peu éclairés. Ses feuilles charnues stockent l\'eau, la rendant très résistante.'
        },
        'Chlorophytum Comosum': {
            'path': 'assets/plants/chlorophytum_comosum.png',
            'species': 'Chlorophytum comosum',
            'description': 'La plante araignée, facile à multiplier avec ses petites pousses. Produit naturellement des rejets que vous pouvez replanter facilement.'
        },
        'Strelitzia Reginae': {
            'path': 'assets/plants/strelitzia_reginae.png',
            'species': 'Strelitzia reginae',
            'description': 'L\'oiseau de paradis, une plante spectaculaire aux fleurs orange et bleues. Peut fleurir en intérieur avec des soins appropriés.'
        },
        'Dracaena Marginata': {
            'path': 'assets/plants/dracaena_marginata.jpg',
            'species': 'Dracaena marginata',
            'description': 'Le dragonnier de Madagascar, un palmier d\'intérieur élégant et résistant. Sa croissance verticale en fait un excellent choix décoratif.'
        }
    }

    # Choix aléatoire d'une plante parmi les 8 disponibles
    name = factory.LazyFunction(
        lambda: random.choice(list(PlantFactory.PLANT_IMAGE_MAPPING.keys()))
    )

    # Espèce et description basées sur le choix
    species = factory.LazyAttribute(
        lambda obj: PlantFactory.PLANT_IMAGE_MAPPING[obj.name]['species']
    )

    description = factory.LazyAttribute(
        lambda obj: PlantFactory.PLANT_IMAGE_MAPPING[obj.name]['description']
    )

    # Image en base64 correspondante
    photo_base64 = factory.LazyAttribute(
        lambda obj: PlantFactory._get_plant_image(obj.name)
    )

    # Propriétaire aléatoire avec priorité aux comptes de base
    @factory.lazy_attribute
    def owner(self):
        """Choisir propriétaire avec priorité aux comptes de base"""
        from factories.user_factory import UserFactory

        # 30% de chance d'utiliser user@arosaje.fr si il existe
        if fake.random_int(1, 100) <= 30:
            test_user = PlantFactory._get_or_create_user_by_email('user@arosaje.fr')
            if test_user:
                return test_user

        # Sinon, créer un utilisateur standard avec bon rôle
        return UserFactory(
            role=fake.random_element([UserRole.USER, UserRole.BOTANIST])
        )

    owner_id = factory.LazyAttribute(lambda obj: obj.owner.id)

    @staticmethod
    def _get_plant_image(plant_name):
        """Récupère l'image base64 pour une plante donnée"""
        if plant_name in PlantFactory.PLANT_IMAGE_MAPPING:
            image_path = PlantFactory.PLANT_IMAGE_MAPPING[plant_name]['path']
            return PlantFactory.image_to_base64(image_path)
        return 'data:image/jpeg;base64,placeholder'

    @classmethod
    def create_all_species(cls, **kwargs):
        """
        Crée une plante de chaque espèce (les 8 vraies images)
        Garantit qu'on a toutes les images utilisées
        """
        plants = []
        for plant_name in cls.PLANT_IMAGE_MAPPING.keys():
            plant = cls.create(name=plant_name, **kwargs)
            plants.append(plant)
        return plants

    @classmethod
    def create_specific_plant(cls, plant_name, **kwargs):
        """
        Crée une plante spécifique par nom

        Args:
            plant_name: Un des noms dans PLANT_IMAGE_MAPPING
        """
        if plant_name not in cls.PLANT_IMAGE_MAPPING:
            raise ValueError(f"Plante inconnue: {plant_name}. Disponibles: {list(cls.PLANT_IMAGE_MAPPING.keys())}")

        return cls.create(name=plant_name, **kwargs)

class MonsteraFactory(PlantFactory):
    """Factory spécialisée pour Monstera Deliciosa"""
    name = "Monstera Deliciosa"

class FicusFactory(PlantFactory):
    """Factory spécialisée pour Ficus Lyrata"""
    name = "Ficus Lyrata"

class SansevieriaFactory(PlantFactory):
    """Factory spécialisée pour Sansevieria Trifasciata"""
    name = "Sansevieria Trifasciata"

class PothosFactory(PlantFactory):
    """Factory spécialisée pour Pothos Doré"""
    name = "Pothos Doré"

class ZamioculcasFactory(PlantFactory):
    """Factory spécialisée pour Zamioculcas Zamiifolia"""
    name = "Zamioculcas Zamiifolia"

class ChlorophytumFactory(PlantFactory):
    """Factory spécialisée pour Chlorophytum Comosum"""
    name = "Chlorophytum Comosum"

class StrelitziaFactory(PlantFactory):
    """Factory spécialisée pour Strelitzia Reginae"""
    name = "Strelitzia Reginae"

class DracaenaFactory(PlantFactory):
    """Factory spécialisée pour Dracaena Marginata"""
    name = "Dracaena Marginata"

# Exports
__all__ = [
    'PlantFactory', 'MonsteraFactory', 'FicusFactory', 'SansevieriaFactory',
    'PothosFactory', 'ZamioculcasFactory', 'ChlorophytumFactory',
    'StrelitziaFactory', 'DracaenaFactory'
]