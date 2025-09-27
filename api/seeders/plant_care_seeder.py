"""
Plant Care Seeder - Création des gardes de plantes pour tests
"""

import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session

from models.plant_care import PlantCare
from models.plant import Plant
from models.user import User
from seeders import BaseSeeder


class PlantCareSeeder(BaseSeeder):
    """Seeder pour créer des gardes de plantes réalistes"""

    def __init__(self):
        super().__init__()
        self.fake = Faker('fr_FR')

    def clear(self):
        """Supprime toutes les gardes existantes"""
        deleted = self.session.query(PlantCare).delete()
        self.session.commit()
        print(f"  OK suppression {deleted} gardes")

    def seed(self, count=15, **kwargs):
        """Méthode principale de seeding (implémentation BaseSeeder)"""
        return self.seed_plant_cares(count)

    def seed_plant_cares(self, count: int = 15):
        """
        Crée des gardes de plantes réalistes avec logique 1 plante = 1 garde

        RÈGLE MÉTIER : Une plante ne peut avoir qu'une seule garde à la fois
        """
        print(f"Demande de création de {count} gardes de plantes...")

        # Récupérer les plantes qui n'ont PAS encore de garde
        plants_without_care = self.session.query(Plant).filter(
            ~Plant.id.in_(
                self.session.query(PlantCare.plant_id).distinct()
            )
        ).all()

        users = self.session.query(User).filter(User.role == 'USER').all()

        if not plants_without_care:
            print("  ❌ Aucune plante disponible pour garde (toutes ont déjà une garde)")
            return

        if not users:
            print("  ❌ Pas d'utilisateurs disponibles")
            return

        # Limiter le count au nombre de plantes disponibles
        actual_count = min(count, len(plants_without_care))
        print(f"  📊 {len(plants_without_care)} plantes disponibles → création de {actual_count} gardes")

        created_count = 0
        locations = [
            "Paris 15e arrondissement", "Lyon 3e", "Marseille centre-ville",
            "Toulouse Capitole", "Nice Vieux Port", "Bordeaux centre",
            "Lille Vieux-Lille", "Strasbourg Petite France", "Nantes centre"
        ]

        # Prendre les premières plantes disponibles
        selected_plants = plants_without_care[:actual_count]

        for plant in selected_plants:
            try:
                # Dates réalistes (passé récent, présent, futur proche)
                days_offset = random.randint(-30, 30)
                start_date = datetime.now() + timedelta(days=days_offset)
                duration = random.randint(7, 21)  # 1-3 semaines
                end_date = start_date + timedelta(days=duration)

                # Status réaliste selon les dates
                now = datetime.now()
                if end_date < now:
                    status = random.choice(['completed', 'completed', 'cancelled'])
                elif start_date > now:
                    status = 'pending'
                elif start_date <= now <= end_date:
                    status = random.choice(['accepted', 'in_progress', 'in_progress'])
                else:
                    status = 'pending'

                care = PlantCare(
                    plant_id=plant.id,
                    owner_id=plant.owner_id,
                    start_date=start_date,
                    end_date=end_date,
                    location=random.choice(locations),
                    care_instructions=self._generate_care_instructions(plant),
                    status=status
                )

                self.session.add(care)
                created_count += 1
                print(f"  ✅ Garde créée pour {plant.name} (ID: {plant.id})")

            except Exception as e:
                print(f"  ⚠️ Erreur garde pour plante {plant.id}: {e}")
                continue

        self.session.commit()
        print(f"  ✅ {created_count} gardes créées (1 plante = 1 garde respecté)")

        # Vérification finale
        total_plants = self.session.query(Plant).count()
        total_cares = self.session.query(PlantCare).count()
        print(f"  📊 État final: {total_plants} plantes, {total_cares} gardes")

    def _generate_care_instructions(self, plant) -> str:
        """Génère des instructions de garde réalistes selon l'espèce"""

        base_instructions = {
            'Monstera Deliciosa': [
                "Arroser quand la terre est sèche en surface",
                "Pulvériser les feuilles pour l'humidité",
                "Éviter le soleil direct, préférer la lumière tamisée"
            ],
            'Ficus Lyrata': [
                "Arroser modérément, laisser sécher entre les arrosages",
                "Nettoyer les feuilles avec un chiffon humide",
                "Placer près d'une fenêtre lumineuse sans soleil direct"
            ],
            'Sansevieria Trifasciata': [
                "Arroser très peu, résistante à la sécheresse",
                "Peut supporter peu de lumière",
                "Attention au sur-arrosage (risque de pourriture)"
            ],
            'Pothos Doré': [
                "Arroser quand la terre sèche légèrement",
                "Peut vivre en suspension ou grimpant",
                "Supporte bien l'ombre partielle"
            ]
        }

        # Instructions selon l'espèce ou génériques
        species_instructions = base_instructions.get(plant.species, [
            "Suivre les besoins habituels de la plante",
            "Surveiller l'état des feuilles",
            "Adapter l'arrosage selon la météo"
        ])

        # Ajouter des instructions personnalisées aléatoires
        extra_instructions = [
            "Contacter en cas de problème",
            "Photos bienvenues pour suivre l'évolution",
            "Fertiliser si nécessaire",
            "Surveiller les parasites",
            "Tourner la plante pour une croissance uniforme"
        ]

        # Combine 2-3 instructions
        selected = random.sample(species_instructions, min(2, len(species_instructions)))
        if random.random() > 0.5:  # 50% de chance d'ajouter une instruction extra
            selected.append(random.choice(extra_instructions))

        return ". ".join(selected) + "."