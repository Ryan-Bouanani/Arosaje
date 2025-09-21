#!/usr/bin/env python3
"""
Utilitaire pour la logique préventive des dates/status des gardes
Fonction réutilisable pour tous les scripts de création de gardes
"""

from datetime import datetime, timedelta
import random

# Adresses réalistes dans diverses villes de France pour les gardes
FRENCH_ADDRESSES = [
    # Paris et région parisienne
    "15 Rue de Rivoli, 75001 Paris",
    "32 Avenue des Champs-Élysées, 75008 Paris",
    "8 Place de la Bastille, 75011 Paris",
    # Lyon
    "25 Rue Victor Hugo, 69002 Lyon",
    "45 Place Bellecour, 69002 Lyon",
    # Marseille
    "67 La Canebière, 13001 Marseille",
    "23 Rue Saint-Ferréol, 13001 Marseille",
    # Toulouse
    "18 Place du Capitole, 31000 Toulouse",
    "54 Rue d'Alsace-Lorraine, 31000 Toulouse",
    # Nice
    "9 Promenade des Anglais, 06000 Nice",
    "41 Avenue Jean Médecin, 06000 Nice",
    # Strasbourg
    "33 Grande Rue, 67000 Strasbourg",
    "19 Place Kléber, 67000 Strasbourg",
    # Bordeaux
    "76 Cours de l'Intendance, 33000 Bordeaux",
    "28 Place de la Bourse, 33000 Bordeaux",
    # Lille
    "14 Rue Nationale, 59000 Lille",
    "52 Grand Place, 59000 Lille",
    # Nantes
    "37 Rue Crébillon, 44000 Nantes",
    "63 Place Royale, 44000 Nantes",
    # Montpellier
    "12 Rue de la Loge, 34000 Montpellier"
]

# Coordonnées correspondant aux villes principales
CITY_COORDINATES = {
    "Paris": (48.8566, 2.3522),
    "Lyon": (45.7640, 4.8357),
    "Marseille": (43.2965, 5.3698),
    "Toulouse": (43.6047, 1.4442),
    "Nice": (43.7102, 7.2620),
    "Strasbourg": (48.5734, 7.7521),
    "Bordeaux": (44.8378, -0.5792),
    "Lille": (50.6292, 3.0573),
    "Nantes": (47.2184, -1.5536),
    "Montpellier": (43.6110, 3.8767)
}

def calculate_dates_by_status(status, duration_days):
    """
    Calcule les dates cohérentes selon le statut de la garde

    Args:
        status (str): Statut de la garde (PENDING, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED)
        duration_days (int): Durée de la garde en jours

    Returns:
        tuple: (start_date, end_date) ou (None, None) pour CANCELLED

    Logique:
        PENDING: start_date futur (3-10 jours), garde proposée
        ACCEPTED: start_date futur (1-5 jours), garde confirmée
        IN_PROGRESS: start_date passé (1-5 jours), garde active
        COMPLETED: start_date et end_date passés, garde terminée
        CANCELLED: garde l'existant, dates non critiques
    """
    now = datetime.now()

    if status == 'PENDING':
        # Garde en attente - commence dans 3-10 jours
        start_date = now + timedelta(days=random.randint(3, 10))
        end_date = start_date + timedelta(days=duration_days)

    elif status == 'ACCEPTED':
        # Garde acceptée - commence dans 1-5 jours
        start_date = now + timedelta(days=random.randint(1, 5))
        end_date = start_date + timedelta(days=duration_days)

    elif status == 'IN_PROGRESS':
        # Garde en cours - a commencé il y a 1-5 jours
        start_date = now - timedelta(days=random.randint(1, 5))
        end_date = start_date + timedelta(days=duration_days)

    elif status == 'COMPLETED':
        # Garde terminée - finie il y a 1-3 jours
        end_date = now - timedelta(days=random.randint(1, 3))
        start_date = end_date - timedelta(days=duration_days)

    elif status == 'CANCELLED':
        # Garde annulée - on garde les dates existantes (retourne None)
        return None, None

    else:
        # Statut inconnu - par défaut PENDING
        print(f"ATTENTION: Statut inconnu '{status}', utilisation de PENDING par défaut")
        start_date = now + timedelta(days=random.randint(3, 10))
        end_date = start_date + timedelta(days=duration_days)

    return start_date, end_date

def validate_status_date_consistency(status, start_date, end_date):
    """
    Valide la cohérence entre un statut et ses dates

    Args:
        status (str): Statut de la garde
        start_date (datetime): Date de début
        end_date (datetime): Date de fin

    Returns:
        tuple: (is_valid, issues_list)
    """
    now = datetime.now()
    issues = []

    # Vérification générale
    if end_date <= start_date:
        issues.append("end_date <= start_date")

    # Vérification par statut
    if status == 'PENDING':
        if start_date <= now:
            issues.append("PENDING mais start_date dans le passé")

    elif status == 'ACCEPTED':
        if start_date <= now:
            issues.append("ACCEPTED mais start_date dans le passé")

    elif status == 'IN_PROGRESS':
        if start_date > now:
            issues.append("IN_PROGRESS mais start_date dans le futur")
        if end_date <= now:
            issues.append("IN_PROGRESS mais end_date dans le passé")

    elif status == 'COMPLETED':
        if end_date > now:
            issues.append("COMPLETED mais end_date dans le futur")
        if start_date > now:
            issues.append("COMPLETED mais start_date dans le futur")

    return len(issues) == 0, issues

def get_random_french_address():
    """Retourne une adresse aléatoire de France"""
    return random.choice(FRENCH_ADDRESSES)

def get_coordinates_from_address(address):
    """Retourne les coordonnées correspondant à une adresse française"""
    # Extraire le nom de la ville de l'adresse
    for city_name, coords in CITY_COORDINATES.items():
        if city_name in address:
            base_lat, base_lon = coords

            # Ajouter une petite variation aléatoire (±2km environ)
            lat_variation = random.randint(-100, 100) / 10000  # ~±1km
            lon_variation = random.randint(-100, 100) / 10000  # ~±1km

            return base_lat + lat_variation, base_lon + lon_variation

    # Fallback vers Lyon si la ville n'est pas trouvée
    return 45.7640 + random.randint(-100, 100) / 10000, 4.8357 + random.randint(-100, 100) / 10000

def get_diverse_location():
    """Retourne une adresse et ses coordonnées pour maximiser la diversité géographique"""
    address = get_random_french_address()
    latitude, longitude = get_coordinates_from_address(address)
    return address, latitude, longitude

# Exemples d'utilisation
if __name__ == "__main__":
    print("=== TESTS DE LA LOGIQUE PRÉVENTIVE ===\n")

    # Test pour chaque statut
    statuses = ['PENDING', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
    duration = 14  # 2 semaines

    for status in statuses:
        start_date, end_date = calculate_dates_by_status(status, duration)

        if start_date is None:
            print(f"{status}: Dates non modifiées (garde annulée)")
        else:
            is_valid, issues = validate_status_date_consistency(status, start_date, end_date)
            validation_status = "OK VALIDE" if is_valid else f"ERREUR PROBLEME: {', '.join(issues)}"

            print(f"{status}: {start_date.strftime('%Y-%m-%d %H:%M')} -> {end_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"  {validation_status}\n")