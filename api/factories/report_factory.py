"""
CareReportFactory - Génération de rapports de garde réalistes
Crée des rapports détaillés avec photos et évaluations
"""

import factory
from datetime import timedelta
from factories.base import BaseFactory
from factories import fake
from models.care_report import CareReport, HealthLevel
from models.plant_care import CareStatus

class CareReportFactory(BaseFactory):
    """
    Factory pour générer des rapports de garde réalistes

    Exemples:
        # Rapport basique
        report = CareReportFactory()

        # Rapport pour garde spécifique
        report = CareReportFactory(plant_care=my_care)

        # Rapport avec santé excellente
        excellent = CareReportFactory(health_level=HealthLevel.EXCELLENT)

        # Lot de rapports
        reports = CareReportFactory.create_batch(10)
    """

    class Meta:
        model = CareReport

    # Garde de plante (seulement pour les gardes IN_PROGRESS ou COMPLETED)
    plant_care = factory.SubFactory(
        'factories.care_factory.InProgressCareFactory'
    )
    plant_care_id = factory.LazyAttribute(lambda obj: obj.plant_care.id)

    # Gardien (celui de la garde)
    caretaker_id = factory.LazyAttribute(lambda obj: obj.plant_care.caretaker_id)

    # Date du rapport (pendant la période de garde)
    @factory.lazy_attribute
    def report_date(self):
        """Date du rapport pendant la période de garde"""
        start = self.plant_care.start_date
        end = self.plant_care.end_date

        # Rapport entre le début et la fin de la garde
        if end > start:
            return fake.date_time_between(start_date=start, end_date=end)
        else:
            # Fallback si les dates sont mal configurées
            return start + timedelta(days=fake.random_int(1, 7))

    # Templates de descriptions par niveau de santé
    HEALTH_DESCRIPTIONS = {
        HealthLevel.EXCELLENT: [
            "Plante en forme exceptionnelle ! Croissance visible et feuillage luxuriant.",
            "État parfait, nouvelles pousses observées. Arrosage optimal maintenu.",
            "Santé excellente, couleurs vives et port majestueux.",
            "Croissance remarquable, aucun signe de stress. Conditions idéales."
        ],
        HealthLevel.GOOD: [
            "Plante en bonne santé générale. Arrosage effectué selon les instructions.",
            "État satisfaisant, quelques feuilles anciennes retirées. Bon développement.",
            "Santé correcte, maintien des soins quotidiens. Évolution positive.",
            "Condition stable, surveillance attentive maintenue."
        ],
        HealthLevel.AVERAGE: [
            "État moyen, quelques signes de stress observés. Ajustements apportés.",
            "Santé acceptable avec surveillance renforcée. Modification des soins.",
            "Condition moyenne, intervention préventive effectuée.",
            "État stable mais nécessite une attention particulière."
        ],
        HealthLevel.CONCERNING: [
            "Signes de stress importants détectés. Mesures correctives appliquées.",
            "État préoccupant, consultation botaniste recommandée urgente.",
            "Dégradation observée, protocole d'urgence activé.",
            "Condition délicate nécessitant intervention spécialisée."
        ],
        HealthLevel.CRITICAL: [
            "État critique ! Intervention d'urgence réalisée.",
            "Situation alarmante, mesures drastiques prises.",
            "Condition très préoccupante, contact propriétaire immédiat.",
            "État critique nécessitant expertise botanique urgente."
        ]
    }

    # Niveau de santé avec distribution réaliste
    health_level = factory.LazyFunction(
        lambda: fake.random_element({
            HealthLevel.EXCELLENT: 0.25,   # 25%
            HealthLevel.GOOD: 0.45,        # 45%
            HealthLevel.AVERAGE: 0.20,     # 20%
            HealthLevel.CONCERNING: 0.08,  # 8%
            HealthLevel.CRITICAL: 0.02     # 2%
        })
    )

    # Description basée sur le niveau de santé
    @factory.lazy_attribute
    def description(self):
        """Description contextuelle selon la santé et la plante"""
        base_desc = fake.random_element(
            self.HEALTH_DESCRIPTIONS[self.health_level]
        )

        # Ajouter contexte spécifique à la plante
        plant_name = getattr(self.plant_care.plant, 'nom', 'cette plante')

        plant_specific = {
            'Monstera Deliciosa': {
                HealthLevel.EXCELLENT: " Nouvelles perforations apparues sur jeunes feuilles.",
                HealthLevel.GOOD: " Feuilles bien hydratées, perforations nettes.",
                HealthLevel.CONCERNING: " Feuilles qui brunissent, exposition ajustée."
            },
            'Ficus Lyrata': {
                HealthLevel.EXCELLENT: " Feuilles brillantes sans taches brunes.",
                HealthLevel.GOOD: " Port dressé maintenu, pas de chute de feuilles.",
                HealthLevel.CONCERNING: " Quelques feuilles jaunies retirées."
            },
            'Sansevieria Trifasciata': {
                HealthLevel.EXCELLENT: " Feuilles droites et fermes, croissance visible.",
                HealthLevel.GOOD: " Résistance habituelle confirmée.",
                HealthLevel.CONCERNING: " Ramollissement détecté, arrosage réduit."
            }
        }

        addition = plant_specific.get(plant_name, {}).get(self.health_level, "")
        return base_desc + addition

    # Photos avant/après (simulées avec placeholders)
    @factory.lazy_attribute
    def photo_before(self):
        """Photo avant soins (85% des rapports)"""
        if fake.boolean(chance_of_getting_true=85):
            # Simuler une photo base64
            return f"data:image/jpeg;base64,photo_avant_{fake.uuid4()[:8]}"
        return None

    @factory.lazy_attribute
    def photo_after(self):
        """Photo après soins (80% des rapports)"""
        if fake.boolean(chance_of_getting_true=80):
            return f"data:image/jpeg;base64,photo_apres_{fake.uuid4()[:8]}"
        return None

class ExcellentReportFactory(CareReportFactory):
    """Factory pour rapports excellents"""
    health_level = HealthLevel.EXCELLENT

class GoodReportFactory(CareReportFactory):
    """Factory pour rapports bons"""
    health_level = HealthLevel.GOOD

class ConcerningReportFactory(CareReportFactory):
    """Factory pour rapports préoccupants"""
    health_level = HealthLevel.CONCERNING

    description = factory.LazyAttribute(
        lambda obj: f"Attention requise pour {obj.plant_care.plant.nom}. "
                   f"Des signes de stress ont été observés. "
                   f"Mesures correctives appliquées et surveillance renforcée."
    )

class CompletedCareReportFactory(CareReportFactory):
    """Factory pour rapports de gardes terminées"""
    plant_care = factory.SubFactory(
        'factories.care_factory.CompletedCareFactory'
    )

    # Date de rapport proche de la fin de garde
    @factory.lazy_attribute
    def report_date(self):
        """Rapport vers la fin de la garde terminée"""
        end_date = self.plant_care.end_date
        # 1-3 jours avant la fin
        offset = timedelta(days=fake.random_int(1, 3))
        return end_date - offset

class DetailedReportFactory(CareReportFactory):
    """Factory pour rapports très détaillés"""

    @factory.lazy_attribute
    def description(self):
        """Description très détaillée avec observations précises"""
        base = super().description

        details = [
            f" Température ambiante: {fake.random_int(18, 24)}°C.",
            f" Humidité: {fake.random_int(40, 70)}%.",
            f" Dernière fertilisation: {fake.date_between(start_date='-30d', end_date='-7d')}.",
            f" pH du sol vérifié: {fake.random_element(['6.0', '6.5', '7.0'])}.",
            f" Inspection des parasites: négative."
        ]

        selected_details = fake.random_elements(details, length=fake.random_int(2, 4))
        return base + "".join(selected_details)

# Exports
__all__ = [
    'CareReportFactory', 'ExcellentReportFactory', 'GoodReportFactory',
    'ConcerningReportFactory', 'CompletedCareReportFactory', 'DetailedReportFactory'
]