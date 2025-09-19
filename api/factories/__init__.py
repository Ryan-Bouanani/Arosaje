"""
Factories pour A'rosa-je avec factory_boy + Faker français
Configuration globale et imports principaux
"""

from faker import Faker
import factory
import random

# Configuration Faker français
fake = Faker('fr_FR')
Faker.seed(42)  # Pour la reproductibilité des tests

# Configuration factory_boy
factory.Faker._DEFAULT_LOCALE = 'fr_FR'

# Listes françaises personnalisées
FRENCH_CITIES = [
    "Paris, France", "Lyon, France", "Marseille, France", "Toulouse, France",
    "Nice, France", "Nantes, France", "Montpellier, France", "Strasbourg, France",
    "Bordeaux, France", "Lille, France", "Rennes, France", "Reims, France",
    "Saint-Étienne, France", "Toulon, France", "Le Havre, France", "Grenoble, France",
    "Dijon, France", "Angers, France", "Villeurbanne, France", "Saint-Denis, France"
]

FRENCH_PLANT_NAMES = [
    "Monstera Deliciosa", "Ficus Lyrata", "Sansevieria Trifasciata",
    "Pothos Doré", "Zamioculcas Zamiifolia", "Chlorophytum Comosum",
    "Strelitzia Reginae", "Dracaena Marginata", "Philodendron Scandens",
    "Calathea Orbifolia", "Alocasia Polly", "Pilea Peperomioides"
]

FRENCH_DOMAINS = [
    'gmail.com', 'yahoo.fr', 'outlook.fr', 'free.fr', 'orange.fr',
    'sfr.fr', 'laposte.net', 'wanadoo.fr', 'hotmail.fr'
]

def random_french_city():
    """Retourne une ville française aléatoire"""
    return random.choice(FRENCH_CITIES)

def random_french_phone():
    """Génère un numéro de téléphone français réaliste"""
    # Format: 0X.XX.XX.XX.XX (mobile ou fixe)
    first_digit = random.choice(['1', '2', '3', '4', '5', '6', '7', '8', '9'])
    remaining = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    phone = f"0{first_digit}{remaining}"
    # Format avec points
    return f"{phone[:2]}.{phone[2:4]}.{phone[4:6]}.{phone[6:8]}.{phone[8:]}"

def random_french_email(first_name, last_name):
    """Génère un email français réaliste"""
    domain = random.choice(FRENCH_DOMAINS)
    # Différents formats d'email
    formats = [
        f"{first_name.lower()}.{last_name.lower()}@{domain}",
        f"{first_name.lower()}{last_name.lower()}@{domain}",
        f"{first_name[0].lower()}.{last_name.lower()}@{domain}",
        f"{first_name.lower()}.{last_name[0].lower()}@{domain}"
    ]
    return random.choice(formats)

def random_plant_name():
    """Retourne un nom de plante français"""
    return random.choice(FRENCH_PLANT_NAMES)

# Exports principaux
__all__ = [
    'fake', 'factory', 'random_french_city', 'random_french_phone',
    'random_french_email', 'random_plant_name', 'FRENCH_CITIES',
    'FRENCH_PLANT_NAMES', 'FRENCH_DOMAINS'
]

# Import des factories pour faciliter l'usage
from .user_factory import UserFactory, BotanistFactory, RegularUserFactory
from .plant_factory import PlantFactory
from .care_factory import PlantCareFactory
from .care_report_factory import CareReportFactory