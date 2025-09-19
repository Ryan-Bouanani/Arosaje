"""
AdviceFactory - Génération de conseils botaniques réalistes
Crée des conseils professionnels avec validation croisée
"""

import factory
from factories.base import BaseFactory
from factories import fake
from models.advice import Advice, AdvicePriority, ValidationStatus
from models.user import UserRole

class AdviceFactory(BaseFactory):
    """
    Factory pour générer des conseils botaniques réalistes

    Exemples:
        # Conseil basique
        advice = AdviceFactory()

        # Conseil urgent
        urgent = AdviceFactory(priority=AdvicePriority.URGENT)

        # Conseil validé
        validated = AdviceFactory(validation_status=ValidationStatus.VALIDATED)

        # Lot de conseils
        advices = AdviceFactory.create_batch(15)
    """

    class Meta:
        model = Advice

    # Garde de plante associée
    plant_care = factory.SubFactory('factories.care_factory.PlantCareFactory')
    plant_care_id = factory.LazyAttribute(lambda obj: obj.plant_care.id)

    # Botaniste auteur
    botanist = factory.SubFactory(
        'factories.user_factory.BotanistFactory',
        role=UserRole.BOTANIST
    )
    botanist_id = factory.LazyAttribute(lambda obj: obj.botanist.id)

    # Templates de conseils professionnels par type de plante
    ADVICE_TEMPLATES = {
        'Monstera Deliciosa': [
            {
                'title': 'Excellent développement des perforations',
                'content': 'Cette Monstera présente un excellent développement de ses fenestrations naturelles. Les feuilles sont bien perforées, signe d\'une plante mature et en bonne santé. Continuez l\'exposition indirecte actuelle.',
                'priority': AdvicePriority.NORMAL
            },
            {
                'title': 'Attention à l\'humidité ambiante',
                'content': 'Les bords des feuilles montrent de légers signes de brunissement, typique d\'un air trop sec. Augmentez l\'humidité en vaporisant régulièrement ou placez un humidificateur près de la plante.',
                'priority': AdvicePriority.NORMAL
            }
        ],
        'Ficus Lyrata': [
            {
                'title': 'Feuillage en parfait état',
                'content': 'Ce Ficus Lyrata présente un feuillage brillant et sans taches, signe d\'un arrosage bien maîtrisé. Maintenez cette routine en laissant sécher le substrat entre deux arrosages.',
                'priority': AdvicePriority.NORMAL
            },
            {
                'title': 'Surveillance hivernale recommandée',
                'content': 'En période hivernale, réduisez la fréquence d\'arrosage car la plante entre en dormance. Un excès d\'eau pourrait provoquer la chute des feuilles.',
                'priority': AdvicePriority.URGENT
            }
        ],
        'Sansevieria Trifasciata': [
            {
                'title': 'Résistance exemplaire',
                'content': 'Cette Sansevieria démontre sa réputation de plante increvable. Les feuilles sont droites et fermes, preuve d\'un entretien adapté. Parfaite pour les débutants.',
                'priority': AdvicePriority.NORMAL
            }
        ],
        'default': [
            {
                'title': 'État général satisfaisant',
                'content': 'Cette plante présente un bon état général. Les feuilles sont vertes et la croissance semble normale. Continuez les soins actuels en surveillant l\'évolution.',
                'priority': AdvicePriority.NORMAL
            },
            {
                'title': 'Observation attentive nécessaire',
                'content': 'Quelques signes de stress observés nécessitent une surveillance accrue. Vérifiez l\'arrosage, l\'exposition et l\'humidité ambiante.',
                'priority': AdvicePriority.URGENT
            }
        ]
    }

    @factory.lazy_attribute
    def title(self):
        """Titre basé sur la plante de la garde"""
        plant_name = getattr(self.plant_care.plant, 'nom', 'default')
        templates = self.ADVICE_TEMPLATES.get(plant_name, self.ADVICE_TEMPLATES['default'])
        chosen_template = fake.random_element(templates)
        return chosen_template['title']

    @factory.lazy_attribute
    def content(self):
        """Contenu détaillé basé sur la plante"""
        plant_name = getattr(self.plant_care.plant, 'nom', 'default')
        templates = self.ADVICE_TEMPLATES.get(plant_name, self.ADVICE_TEMPLATES['default'])
        chosen_template = fake.random_element(templates)
        return chosen_template['content']

    @factory.lazy_attribute
    def priority(self):
        """Priorité basée sur le template choisi"""
        plant_name = getattr(self.plant_care.plant, 'nom', 'default')
        templates = self.ADVICE_TEMPLATES.get(plant_name, self.ADVICE_TEMPLATES['default'])
        chosen_template = fake.random_element(templates)
        return chosen_template['priority']

    # Statut de validation (70% validés, 30% en attente)
    validation_status = factory.LazyFunction(
        lambda: fake.random_element({
            ValidationStatus.VALIDATED: 0.7,
            ValidationStatus.PENDING: 0.3
        })
    )

    # Validateur (un autre botaniste si validé)
    @factory.lazy_attribute
    def validator_id(self):
        """Validateur différent de l'auteur si conseils validé"""
        if self.validation_status == ValidationStatus.VALIDATED:
            from factories.user_factory import BotanistFactory
            # Créer un autre botaniste
            validator = BotanistFactory()
            # S'assurer qu'il est différent de l'auteur
            attempt = 0
            while validator.id == self.botanist_id and attempt < 5:
                validator = BotanistFactory()
                attempt += 1
            return validator.id
        return None

    # Commentaire de validation
    @factory.lazy_attribute
    def validation_comment(self):
        """Commentaire du validateur si validé"""
        if self.validation_status == ValidationStatus.VALIDATED:
            comments = [
                "Diagnostic pertinent et conseils appropriés.",
                "Excellente analyse de l'état de la plante.",
                "Recommandations conformes aux bonnes pratiques.",
                "Conseil validé, approche professionnelle.",
                "Diagnostic précis, suite logique des observations."
            ]
            return fake.random_element(comments)
        return None

    # Date de validation
    validated_at = factory.LazyAttribute(
        lambda obj: fake.date_time_between(start_date='-30d', end_date='now')
        if obj.validation_status == ValidationStatus.VALIDATED else None
    )

    # Version et statut
    version = 1
    is_current_version = True
    previous_version_id = None

    # Notifications
    owner_notified = factory.LazyFunction(lambda: fake.boolean(chance_of_getting_true=80))
    botanist_notified = True

class ValidatedAdviceFactory(AdviceFactory):
    """Factory pour conseils validés"""
    validation_status = ValidationStatus.VALIDATED

class UrgentAdviceFactory(AdviceFactory):
    """Factory pour conseils urgents"""
    priority = AdvicePriority.URGENT

    title = "Intervention urgente recommandée"
    content = factory.LazyAttribute(
        lambda obj: f"Cette plante nécessite une attention immédiate. "
                   f"Des signes de stress importants ont été observés. "
                   f"Vérifiez l'arrosage et l'exposition de toute urgence."
    )

class FollowUpAdviceFactory(AdviceFactory):
    """Factory pour conseils de suivi"""
    priority = AdvicePriority.FOLLOW_UP

    title = "Suivi d'évolution nécessaire"
    content = "L'état de cette plante nécessite un suivi régulier. " \
              "Prenez des photos hebdomadaires pour documenter l'évolution."

class PendingAdviceFactory(AdviceFactory):
    """Factory pour conseils en attente de validation"""
    validation_status = ValidationStatus.PENDING
    validator_id = None
    validation_comment = None
    validated_at = None

# Exports
__all__ = [
    'AdviceFactory', 'ValidatedAdviceFactory', 'UrgentAdviceFactory',
    'FollowUpAdviceFactory', 'PendingAdviceFactory'
]