"""
PlantCareFactory - Génération de gardes de plantes réalistes
Crée des scénarios cohérents avec dates et statuts logiques
"""

import factory
from datetime import datetime, timedelta
from factories.base import BaseFactory
from factories import fake, random_french_city
from models.plant_care import PlantCare, CareStatus
from models.user import UserRole

class PlantCareFactory(BaseFactory):
    """
    Factory pour générer des gardes de plantes réalistes

    Exemples:
        # Garde basique
        care = PlantCareFactory()

        # Garde en cours
        current_care = PlantCareFactory(status=CareStatus.IN_PROGRESS)

        # Garde terminée
        completed = PlantCareFactory(status=CareStatus.COMPLETED)

        # Lot de gardes
        cares = PlantCareFactory.create_batch(20)
    """

    class Meta:
        model = PlantCare

    # Plante et propriétaire
    plant = factory.SubFactory('factories.plant_factory.PlantFactory')
    plant_id = factory.LazyAttribute(lambda obj: obj.plant.id)

    owner = factory.LazyAttribute(lambda obj: obj.plant.owner)
    owner_id = factory.LazyAttribute(lambda obj: obj.owner.id)

    # Gardien différent du propriétaire (sauf pour PENDING)
    caretaker = factory.SubFactory(
        'factories.user_factory.RegularUserFactory',
        role=UserRole.USER
    )

    @factory.lazy_attribute
    def caretaker_id(self):
        """Le gardien doit être différent du propriétaire"""
        if self.status == CareStatus.PENDING:
            return None  # Pas encore de gardien assigné

        # Priorité aux comptes de base user@arosaje.fr (20% de chance)
        if fake.random_int(1, 100) <= 20:
            test_user = PlantCareFactory._get_or_create_user_by_email('user@arosaje.fr')
            if test_user and test_user.id != self.owner_id:
                return test_user.id

        # Pour les autres statuts, retourner l'ID du gardien
        return self.caretaker.id if hasattr(self, 'caretaker') and self.caretaker else None

    # Statut avec distribution réaliste
    status = factory.LazyFunction(
        lambda: fake.random_element([
            CareStatus.COMPLETED,    # Plus fréquent
            CareStatus.COMPLETED,
            CareStatus.IN_PROGRESS,
            CareStatus.ACCEPTED,
            CareStatus.PENDING,
            CareStatus.CANCELLED     # Moins fréquent
        ])
    )

    # Dates cohérentes selon le statut
    @factory.lazy_attribute
    def start_date(self):
        """Date de début basée sur le statut"""
        now = datetime.now()

        if self.status == CareStatus.COMPLETED:
            # Garde terminée : dans le passé
            return fake.date_time_between(start_date='-60d', end_date='-10d')
        elif self.status == CareStatus.IN_PROGRESS:
            # Garde en cours : a commencé récemment
            return fake.date_time_between(start_date='-7d', end_date='now')
        elif self.status == CareStatus.ACCEPTED:
            # Garde acceptée : commence bientôt
            return fake.date_time_between(start_date='now', end_date='+30d')
        elif self.status in [CareStatus.PENDING, CareStatus.CANCELLED]:
            # Garde en attente/annulée : peut être future
            return fake.date_time_between(start_date='+1d', end_date='+45d')

    @factory.lazy_attribute
    def end_date(self):
        """Date de fin cohérente avec le début (7-21 jours plus tard)"""
        duration = fake.random_int(min=7, max=21)  # 1-3 semaines
        return self.start_date + timedelta(days=duration)

    # Localisation française
    location = factory.LazyFunction(random_french_city)

    # Coordonnées GPS basées sur la ville
    @factory.lazy_attribute
    def latitude(self):
        """Génère latitude selon la ville avec dispersion réaliste"""
        return self._get_city_coordinates()[0]

    @factory.lazy_attribute
    def longitude(self):
        """Génère longitude selon la ville avec dispersion réaliste"""
        return self._get_city_coordinates()[1]

    def _get_city_coordinates(self):
        """Retourne coordonnées GPS avec dispersion pour simulation quartiers"""
        import random

        # Coordonnées centres + dispersion par ville
        city_coords = {
            'Paris, France': (48.8566, 2.3522, 0.1),
            'Lyon, France': (45.7640, 4.8357, 0.08),
            'Marseille, France': (43.2965, 5.3698, 0.08),
            'Toulouse, France': (43.6047, 1.4442, 0.08),
            'Nice, France': (43.7102, 7.2620, 0.06),
            'Nantes, France': (47.2184, -1.5536, 0.06),
            'Montpellier, France': (43.6110, 3.8767, 0.06),
            'Strasbourg, France': (48.5734, 7.7521, 0.06),
            'Bordeaux, France': (44.8378, -0.5792, 0.08),
            'Lille, France': (50.6292, 3.0573, 0.06),
            'Rennes, France': (48.1173, -1.6778, 0.06),
            'Reims, France': (49.2583, 4.0317, 0.05),
            'Le Havre, France': (49.4944, 0.1079, 0.05),
            'Saint-Étienne, France': (45.4397, 4.3872, 0.05),
            'Tours, France': (47.3941, 0.6848, 0.05),
            'Amiens, France': (49.8951, 2.2956, 0.05),
            'Limoges, France': (45.8336, 1.2611, 0.05),
            'Angers, France': (47.4784, -0.5632, 0.05),
            'Dijon, France': (47.3220, 5.0415, 0.05),
            'Brest, France': (48.3904, -4.4861, 0.05),
            'Clermont-Ferrand, France': (45.7797, 3.0863, 0.05),
            'Orléans, France': (47.9029, 1.9093, 0.05),
            'Metz, France': (49.1193, 6.1757, 0.05),
            'Rouen, France': (49.4431, 1.0993, 0.05),
            'Perpignan, France': (42.6886, 2.8948, 0.04),
            'Caen, France': (49.1829, -0.3707, 0.05),
            'Besançon, France': (47.2380, 6.0240, 0.04),
            'Villeurbanne, France': (45.7640, 4.8357, 0.05)  # Proche Lyon
        }

        # Récupérer coordonnées de base ou utiliser Paris par défaut
        lat_base, lng_base, dispersion = city_coords.get(
            self.location,
            (48.8566, 2.3522, 0.1)  # Paris par défaut
        )

        # Ajouter dispersion aléatoire pour simuler différents quartiers
        lat_offset = (random.random() - 0.5) * dispersion
        lng_offset = (random.random() - 0.5) * dispersion

        return (
            round(lat_base + lat_offset, 6),
            round(lng_base + lng_offset, 6)
        )

    # Instructions de garde contextuelles
    @factory.lazy_attribute
    def care_instructions(self):
        """Instructions basées sur la plante et le scénario"""
        plant_name = self.plant.nom if hasattr(self.plant, 'nom') else "cette plante"

        base_instructions = {
            'Monstera Deliciosa': "Arroser 2 fois par semaine, exposition indirecte, vaporiser les feuilles",
            'Ficus Lyrata': "Éviter les courants d'air, arrosage quand le sol est sec en surface",
            'Sansevieria Trifasciata': "Très peu d'arrosage, tolère la sécheresse, plante très résistante",
            'Pothos Doré': "Arrosage régulier, peut être cultivé dans l'eau ou en terre",
            'Zamioculcas Zamiifolia': "Arrosage très espacé, tolère la négligence, croissance lente",
            'Chlorophytum Comosum': "Arrosage régulier, produit naturellement des rejets à replanter",
            'Strelitzia Reginae': "Lumière vive, arrosage modéré, humidité élevée pour la floraison",
            'Dracaena Marginata': "Arrosage modéré, lumière indirecte, tailler les feuilles sèches"
        }

        instruction = base_instructions.get(plant_name, "Arrosage selon les besoins de la plante")

        # Ajouter contexte selon statut
        if self.status == CareStatus.IN_PROGRESS:
            instruction += ". Garde actuellement en cours, tout se passe bien."
        elif self.status == CareStatus.PENDING:
            instruction += ". Recherche gardien expérimenté pour cette période."
        elif self.status == CareStatus.COMPLETED:
            instruction += ". Garde terminée avec succès."

        return instruction

    # Conversation (peut être None)
    conversation_id = None

class CompletedCareFactory(PlantCareFactory):
    """Factory pour gardes terminées"""
    status = CareStatus.COMPLETED

    start_date = factory.LazyFunction(
        lambda: fake.date_time_between(start_date='-90d', end_date='-15d')
    )

class InProgressCareFactory(PlantCareFactory):
    """Factory pour gardes en cours"""
    status = CareStatus.IN_PROGRESS

    start_date = factory.LazyFunction(
        lambda: fake.date_time_between(start_date='-10d', end_date='-1d')
    )

class PendingCareFactory(PlantCareFactory):
    """Factory pour gardes en attente"""
    status = CareStatus.PENDING
    caretaker_id = None  # Pas de gardien assigné

    start_date = factory.LazyFunction(
        lambda: fake.date_time_between(start_date='+1d', end_date='+60d')
    )

class AcceptedCareFactory(PlantCareFactory):
    """Factory pour gardes acceptées (futures)"""
    status = CareStatus.ACCEPTED

    start_date = factory.LazyFunction(
        lambda: fake.date_time_between(start_date='+1d', end_date='+30d')
    )

class UrgentCareFactory(PlantCareFactory):
    """Factory pour gardes urgentes (départ imminent)"""
    status = CareStatus.PENDING

    start_date = factory.LazyFunction(
        lambda: fake.date_time_between(start_date='+1d', end_date='+7d')
    )

    care_instructions = factory.LazyAttribute(
        lambda obj: f"URGENCE - Départ imminent ! {obj.plant.nom} nécessite des soins attentifs."
    )

# Exports
__all__ = [
    'PlantCareFactory', 'CompletedCareFactory', 'InProgressCareFactory',
    'PendingCareFactory', 'AcceptedCareFactory', 'UrgentCareFactory'
]