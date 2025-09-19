"""
CareReportFactory - Génération de rapports de séance réalistes
Crée des rapports avec images et évaluations de santé cohérentes
"""

import factory
from datetime import datetime, timedelta
from factories.base import BaseFactory
from factories import fake
from models.care_report import CareReport, HealthLevel
from models.plant_care import CareStatus

class CareReportFactory(BaseFactory):
    """
    Factory pour générer des rapports de séance réalistes avec images

    Exemples:
        # Rapport basique
        report = CareReportFactory()

        # Rapport pour une garde spécifique
        report = CareReportFactory(plant_care=my_care)

        # Lot de rapports
        reports = CareReportFactory.create_batch(10)
    """

    class Meta:
        model = CareReport

    # Garde de plante (doit être fournie)
    plant_care = factory.SubFactory('factories.care_factory.PlantCareFactory')
    plant_care_id = factory.LazyAttribute(lambda obj: obj.plant_care.id)

    # Gardien (même que la garde)
    caretaker_id = factory.LazyAttribute(lambda obj: obj.plant_care.caretaker_id)

    # Date de séance pendant la période de garde
    @factory.lazy_attribute
    def session_date(self):
        """Date du rapport pendant la garde"""
        care = self.plant_care

        if care.status == CareStatus.COMPLETED:
            # Garde terminée : rapport pendant la garde
            duration = (care.end_date - care.start_date).days
            if duration > 0:
                random_day = fake.random_int(1, duration)
                return care.start_date + timedelta(days=random_day)
            else:
                return care.start_date + timedelta(hours=fake.random_int(1, 23))
        elif care.status == CareStatus.IN_PROGRESS:
            # Garde en cours : rapport récent
            days_since_start = max(1, (datetime.now() - care.start_date).days)
            random_day = fake.random_int(1, min(days_since_start, 7))
            return care.start_date + timedelta(days=random_day)
        else:
            # Autres statuts : date récente
            return fake.date_time_between(start_date='-7d', end_date='now')

    # Image de la plante (basée sur la plante de la garde)
    @factory.lazy_attribute
    def photo_base64(self):
        """Image base64 basée sur la plante de la garde"""
        from factories.plant_factory import PlantFactory

        if hasattr(self.plant_care, 'plant') and self.plant_care.plant:
            plant_name = self.plant_care.plant.nom
            image = PlantFactory._get_plant_image(plant_name)

            if image and image != 'data:image/jpeg;base64,placeholder':
                return image

        # Image par défaut si pas trouvée
        return PlantFactory._get_plant_image("Monstera Deliciosa")

    # Niveaux de santé réalistes (plutôt positifs)
    health_level = factory.LazyFunction(
        lambda: fake.random_element([
            HealthLevel.BON,      # 60%
            HealthLevel.BON,
            HealthLevel.BON,
            HealthLevel.MOYEN,    # 30%
            HealthLevel.MOYEN,
            HealthLevel.BAS       # 10%
        ])
    )

    hydration_level = factory.LazyFunction(
        lambda: fake.random_element([
            HealthLevel.BON,      # 60%
            HealthLevel.BON,
            HealthLevel.BON,
            HealthLevel.MOYEN,    # 30%
            HealthLevel.MOYEN,
            HealthLevel.BAS       # 10%
        ])
    )

    vitality_level = factory.LazyFunction(
        lambda: fake.random_element([
            HealthLevel.BON,      # 60%
            HealthLevel.BON,
            HealthLevel.BON,
            HealthLevel.MOYEN,    # 30%
            HealthLevel.MOYEN,
            HealthLevel.BAS       # 10%
        ])
    )

    # Description contextuelle
    @factory.lazy_attribute
    def description(self):
        """Description basée sur la plante et les niveaux de santé"""
        if hasattr(self.plant_care, 'plant') and self.plant_care.plant:
            plant_name = self.plant_care.plant.nom
        else:
            plant_name = "la plante"

        # Descriptions selon l'état général
        if (self.health_level == HealthLevel.BON and
            self.hydration_level == HealthLevel.BON and
            self.vitality_level == HealthLevel.BON):
            descriptions = [
                f"Excellent état de {plant_name}. Arrosage effectué selon planning.",
                f"Contrôle quotidien de {plant_name}. Tout va parfaitement bien !",
                f"Entretien de {plant_name} réalisé. Feuillage magnifique.",
                f"Inspection de {plant_name}. Croissance optimale observée."
            ]
        elif HealthLevel.MOYEN in [self.health_level, self.hydration_level, self.vitality_level]:
            descriptions = [
                f"État correct de {plant_name}. Surveillance renforcée.",
                f"Entretien de {plant_name}. Quelques ajustements nécessaires.",
                f"Contrôle de {plant_name}. Amélioration en cours.",
                f"Soins apportés à {plant_name}. Évolution positive."
            ]
        else:
            descriptions = [
                f"Attention particulière pour {plant_name}. Soins intensifiés.",
                f"Surveillance accrue de {plant_name}. Mesures correctives prises.",
                f"État de {plant_name} à surveiller. Propriétaire informé.",
                f"Soins spéciaux pour {plant_name}. Suivi quotidien."
            ]

        return fake.random_element(descriptions)

    # Dates de création
    created_at = factory.LazyAttribute(lambda obj: obj.session_date)

class HealthyReportFactory(CareReportFactory):
    """Factory pour rapports avec plantes en excellente santé"""
    health_level = HealthLevel.BON
    hydration_level = HealthLevel.BON
    vitality_level = HealthLevel.BON

class ConcernedReportFactory(CareReportFactory):
    """Factory pour rapports avec plantes nécessitant attention"""
    health_level = factory.LazyFunction(
        lambda: fake.random_element([HealthLevel.MOYEN, HealthLevel.BAS])
    )
    hydration_level = factory.LazyFunction(
        lambda: fake.random_element([HealthLevel.MOYEN, HealthLevel.BAS])
    )
    vitality_level = factory.LazyFunction(
        lambda: fake.random_element([HealthLevel.MOYEN, HealthLevel.BAS])
    )

class RecentReportFactory(CareReportFactory):
    """Factory pour rapports récents (derniers 3 jours)"""
    session_date = factory.LazyFunction(
        lambda: fake.date_time_between(start_date='-3d', end_date='now')
    )

# Exports
__all__ = [
    'CareReportFactory', 'HealthyReportFactory',
    'ConcernedReportFactory', 'RecentReportFactory'
]