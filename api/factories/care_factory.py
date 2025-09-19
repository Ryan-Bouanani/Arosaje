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

        # S'assurer que gardien ≠ propriétaire
        attempt = 0
        while self.caretaker.id == self.owner_id and attempt < 10:
            from factories.user_factory import RegularUserFactory
            self.caretaker = RegularUserFactory(role=UserRole.USER)
            attempt += 1

        return self.caretaker.id

    # Statut avec distribution réaliste
    status = factory.LazyFunction(
        lambda: fake.random_element({
            CareStatus.COMPLETED: 0.4,    # 40% terminées
            CareStatus.IN_PROGRESS: 0.2,  # 20% en cours
            CareStatus.ACCEPTED: 0.2,     # 20% acceptées
            CareStatus.PENDING: 0.15,     # 15% en attente
            CareStatus.CANCELLED: 0.05    # 5% annulées
        })
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