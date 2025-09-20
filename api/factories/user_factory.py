"""
UserFactory - Génération d'utilisateurs français réalistes
Utilise Faker français pour créer des données authentiques
"""

import factory
from factories.base import BaseFactory
from factories import fake, random_french_city, random_french_phone, random_french_email
from models.user import User, UserRole
from utils.password import get_password_hash

class UserFactory(BaseFactory):
    """
    Factory pour générer des utilisateurs français réalistes

    Exemples:
        # Utilisateur standard
        user = UserFactory()

        # Botaniste spécifique
        botanist = UserFactory(role=UserRole.BOTANIST)

        # Lot d'utilisateurs
        users = UserFactory.create_batch(10)

        # Utilisateur dans une ville spécifique
        parisian = UserFactory(location="Paris, France")
    """

    class Meta:
        model = User

    # Noms français réalistes
    first_name = factory.Faker('first_name', locale='fr_FR')
    last_name = factory.Faker('last_name', locale='fr_FR')

    # Compatibilité avec colonnes françaises existantes
    prenom = factory.LazyAttribute(lambda obj: obj.first_name)
    nom = factory.LazyAttribute(lambda obj: obj.last_name)

    # Email généré à partir du nom (évite les doublons)
    email = factory.LazyAttribute(
        lambda obj: random_french_email(obj.first_name, obj.last_name)
    )

    # Mot de passe par défaut
    password = factory.LazyFunction(lambda: get_password_hash('epsi691'))

    # Localisation française
    location = factory.LazyFunction(random_french_city)
    localisation = factory.LazyAttribute(lambda obj: obj.location)  # Compatibilité

    # Téléphone français
    telephone = factory.LazyFunction(random_french_phone)

    # Rôle par défaut USER (85%), quelques BOTANIST (15%)
    role = factory.LazyFunction(
        lambda: UserRole.BOTANIST if fake.random_int(1, 100) <= 15 else UserRole.USER
    )

    # Compte vérifié par défaut
    is_verified = True

    @factory.post_generation
    def ensure_unique_email(obj, create, extracted, **kwargs):
        """
        Post-traitement pour s'assurer que l'email est unique
        En cas de conflit, ajoute un nombre aléatoire
        """
        if create:
            # Utiliser la session de la factory pour vérifier unicité
            from sqlalchemy import exists

            # Utiliser la session de la factory au lieu d'en créer une nouvelle
            session = UserFactory._meta.sqlalchemy_session
            attempt = 0
            original_email = obj.email

            while session.query(exists().where(User.email == obj.email)).scalar():
                attempt += 1
                # Ajouter un nombre pour rendre unique
                name_part, domain = original_email.split('@')
                obj.email = f"{name_part}{attempt}@{domain}"

                # Sécurité : éviter boucle infinie
                if attempt > 100:
                    obj.email = f"{fake.uuid4()}@gmail.com"
                    break

class AdminUserFactory(UserFactory):
    """Factory spécialisée pour les administrateurs"""
    role = UserRole.ADMIN
    email = factory.Sequence(lambda n: f"admin{n}@arosaje.fr")
    location = "Paris, France"  # Admins basés à Paris

class BotanistFactory(UserFactory):
    """Factory spécialisée pour les botanistes"""
    role = UserRole.BOTANIST

    # Email professionnel pour botanistes
    email = factory.LazyAttribute(
        lambda obj: f"dr.{obj.first_name.lower()}.{obj.last_name.lower()}@jardin-{fake.city().lower().replace(' ', '')}.fr"
    )

    # Botanistes dans grandes villes avec jardins botaniques
    location = factory.LazyFunction(
        lambda: fake.random_element([
            "Paris, France", "Lyon, France", "Toulouse, France",
            "Bordeaux, France", "Montpellier, France", "Strasbourg, France"
        ])
    )

class RegularUserFactory(UserFactory):
    """Factory spécialisée pour les utilisateurs standards"""
    role = UserRole.USER

# Exports
__all__ = ['UserFactory', 'AdminUserFactory', 'BotanistFactory', 'RegularUserFactory']