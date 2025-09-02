from passlib.context import CryptContext
import re
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe en clair correspond au hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Génère un hash du mot de passe"""
    return pwd_context.hash(password)


def validate_password_policy(password: str) -> tuple[bool, List[str]]:
    """
    Valide la politique de mot de passe CNIL :
    - Minimum 14 caractères
    - Au moins une majuscule
    - Au moins une minuscule
    - Au moins un chiffre
    - Caractères spéciaux optionnels (non obligatoires)

    Returns:
        tuple: (is_valid: bool, errors: List[str])
    """
    errors = []

    # Vérification de la longueur minimum (14 caractères)
    if len(password) < 14:
        errors.append("Le mot de passe doit contenir au minimum 14 caractères")

    # Vérification de la présence d'au moins une majuscule
    if not re.search(r"[A-Z]", password):
        errors.append("Le mot de passe doit contenir au moins une majuscule")

    # Vérification de la présence d'au moins une minuscule
    if not re.search(r"[a-z]", password):
        errors.append("Le mot de passe doit contenir au moins une minuscule")

    # Vérification de la présence d'au moins un chiffre
    if not re.search(r"[0-9]", password):
        errors.append("Le mot de passe doit contenir au moins un chiffre")

    # Pas de caractères interdits (optionnel - actuellement aucune restriction)

    is_valid = len(errors) == 0
    return is_valid, errors
