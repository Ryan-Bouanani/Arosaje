"""
Advice Seeder - Création des conseils botaniques pour tests
"""

import random
from faker import Faker
from sqlalchemy.orm import Session

from models.advice import Advice
from models.plant_care import PlantCare
from models.user import User
from seeders import BaseSeeder


class AdviceSeeder(BaseSeeder):
    """Seeder pour créer des conseils botaniques réalistes"""

    def __init__(self):
        super().__init__()
        self.fake = Faker('fr_FR')

    def clear(self):
        """Supprime tous les conseils existants"""
        deleted = self.session.query(Advice).delete()
        self.session.commit()
        print(f"  OK suppression {deleted} conseils")

    def seed(self, count=10, **kwargs):
        """Méthode principale de seeding (implémentation BaseSeeder)"""
        return self.seed_advice(count)

    def seed_advice(self, count: int = 10):
        """Crée des conseils botaniques réalistes"""
        print(f"Création de {count} conseils botaniques...")

        # Récupérer gardes et botanistes disponibles
        plant_cares = self.session.query(PlantCare).all()
        botanists = self.session.query(User).filter(User.role == 'BOTANIST').all()

        if not plant_cares or not botanists:
            print("  ❌ Pas assez de gardes ou de botanistes")
            return

        created_count = 0

        # Sélectionner des gardes aléatoires pour les conseils
        selected_cares = random.sample(plant_cares, min(count, len(plant_cares)))

        for i, care in enumerate(selected_cares):
            try:
                botanist = random.choice(botanists)
                plant = care.plant

                advice_data = self._generate_advice_for_plant(plant)

                # Statut de validation réaliste
                validation_status = random.choices(
                    ['pending', 'validated', 'rejected'],
                    weights=[60, 35, 5]  # Plus de pending et validated
                )[0]

                validator_id = None
                if validation_status in ['validated', 'rejected']:
                    # Choisir un autre botaniste comme validateur
                    other_botanists = [b for b in botanists if b.id != botanist.id]
                    if other_botanists:
                        validator_id = random.choice(other_botanists).id

                advice = Advice(
                    plant_care_id=care.id,
                    botanist_id=botanist.id,
                    title=advice_data['title'],
                    content=advice_data['content'],
                    priority=random.choice(['normal', 'urgent', 'follow_up']),
                    validation_status=validation_status,
                    validator_id=validator_id,
                    validation_comment=self._generate_validation_comment() if validator_id else None,
                    version=1,
                    is_current_version=True,
                    owner_notified=random.choice([True, False]),
                    botanist_notified=random.choice([True, False])
                )

                self.session.add(advice)
                created_count += 1

            except Exception as e:
                print(f"  ⚠️ Erreur conseil {i+1}: {e}")
                continue

        self.session.commit()
        print(f"  OK {created_count} conseils botaniques créés")

    def _generate_advice_for_plant(self, plant) -> dict:
        """Génère un conseil spécialisé selon l'espèce de plante"""

        advice_templates = {
            'Monstera Deliciosa': {
                'titles': [
                    "Optimisation de l'humidité",
                    "Gestion de la croissance",
                    "Prévention des feuilles jaunes",
                    "Support pour les tiges"
                ],
                'contents': [
                    "Votre Monstera nécessite une humidité élevée. Placez un plateau d'eau près de la plante ou utilisez un humidificateur. Pulvérisez régulièrement les feuilles avec de l'eau non calcaire.",
                    "Cette plante grimpante bénéficiera d'un tuteur mousse. Attachez délicatement les tiges sans serrer. Cela encouragera la production de feuilles plus grandes.",
                    "Les feuilles jaunes indiquent souvent un sur-arrosage. Vérifiez que le drainage est bon et laissez sécher la terre entre les arrosages.",
                    "Nettoyez régulièrement les feuilles avec un chiffon humide pour optimiser la photosynthèse. Évitez les produits lustrants commerciaux."
                ]
            },
            'Ficus Lyrata': {
                'titles': [
                    "Stabilité environnementale",
                    "Prévention de la chute des feuilles",
                    "Optimisation de la lumière",
                    "Gestion du stress hydrique"
                ],
                'contents': [
                    "Le Ficus Lyrata déteste les changements. Évitez de le déplacer et maintenez une température constante entre 18-24°C. Protégez-le des courants d'air.",
                    "La chute des feuilles est souvent due au stress hydrique. Arrosez quand les 2-3 premiers cm de terre sont secs. Utilisez de l'eau à température ambiante.",
                    "Placez votre Ficus près d'une fenêtre exposée est ou ouest. Il a besoin de lumière vive mais pas de soleil direct qui brûlerait ses feuilles.",
                    "En hiver, réduisez les arrosages car la croissance ralentit. Surveillez l'humidité ambiante avec le chauffage qui assèche l'air."
                ]
            },
            'Sansevieria Trifasciata': {
                'titles': [
                    "Prévention de la pourriture",
                    "Gestion des arrosages",
                    "Propagation naturelle",
                    "Adaptation saisonnière"
                ],
                'contents': [
                    "Cette plante redoute l'excès d'eau. Assurez-vous que le pot a un bon drainage. En cas de doute, abstenez-vous d'arroser plutôt que de risquer la pourriture.",
                    "Arrosez seulement quand la terre est complètement sèche, soit environ une fois par mois. En hiver, espacez encore plus les arrosages.",
                    "Les Sansevierias produisent naturellement des rejets à la base. Vous pouvez les séparer délicatement pour multiplier la plante.",
                    "Cette plante s'adapte à presque tous les environnements. Elle tolère la faible luminosité mais préfère une lumière indirecte vive."
                ]
            },
            'Pothos Doré': {
                'titles': [
                    "Taille et façonnage",
                    "Propagation par bouturage",
                    "Gestion de la lumière",
                    "Entretien des feuilles"
                ],
                'contents': [
                    "Taillez régulièrement les tiges trop longues pour encourager la ramification. Coupez juste au-dessus d'un nœud pour favoriser de nouvelles pousses.",
                    "Le Pothos se bouture très facilement dans l'eau. Coupez une tige avec 2-3 nœuds et placez-la dans un verre d'eau. Les racines apparaîtront en 1-2 semaines.",
                    "Bien qu'adaptable, votre Pothos gardera ses panachures dorées avec une lumière vive indirecte. Trop d'ombre fera reverdir les feuilles.",
                    "Dépoussiérez les feuilles régulièrement et retirez celles qui jaunissent. Cette plante dépolluante apprécie une douche tiède occasionnelle."
                ]
            }
        }

        # Conseils génériques si l'espèce n'est pas dans les templates
        generic_advice = {
            'titles': [
                "Diagnostic général de la plante",
                "Conseils d'entretien saisonniers",
                "Prévention des maladies",
                "Optimisation de la croissance"
            ],
            'contents': [
                "Observez attentivement votre plante : couleur des feuilles, fermeté des tiges, état du substrat. Ces indicateurs vous renseignent sur sa santé générale.",
                "Adaptez vos soins selon la saison. Réduisez arrosages et fertilisation en hiver, augmentez la surveillance en été.",
                "Inspectez régulièrement le revers des feuilles pour détecter parasites et maladies. Un traitement précoce est toujours plus efficace.",
                "Une plante bien installée dans son environnement montre une croissance régulière et un feuillage sain. Patience et constance sont clés."
            ]
        }

        # Sélectionner le template approprié
        species_templates = advice_templates.get(plant.species, generic_advice)

        title = random.choice(species_templates['titles'])
        content = random.choice(species_templates['contents'])

        return {'title': title, 'content': content}

    def _generate_validation_comment(self) -> str:
        """Génère un commentaire de validation réaliste"""
        positive_comments = [
            "Conseil pertinent et bien argumenté",
            "Approche méthodologique excellente",
            "Diagnostic précis, recommandations adaptées",
            "Conseil complet et pratique",
            "Bonne prise en compte des spécificités de l'espèce"
        ]

        negative_comments = [
            "Manque de précision dans les recommandations",
            "Pourrait être plus spécifique à l'espèce",
            "Conseil trop généraliste",
            "Nécessite plus de détails pratiques"
        ]

        return random.choice(positive_comments + negative_comments)