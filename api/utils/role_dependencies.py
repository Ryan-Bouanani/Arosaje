"""
Dependencies pour la vérification des rôles utilisateur
Centralise la logique de sécurité basée sur les rôles
"""
from fastapi import Depends, HTTPException, status
from models.user import User, UserRole
from utils.security import get_current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Vérifie que l'utilisateur a le rôle ADMIN

    Args:
        current_user: Utilisateur authentifié

    Returns:
        User: L'utilisateur si admin

    Raises:
        HTTPException: Si pas admin (403)

    Example:
        @router.get("/admin/stats")
        async def get_stats(user: User = Depends(require_admin)):
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user


def require_botanist(current_user: User = Depends(get_current_user)) -> User:
    """
    Vérifie que l'utilisateur a le rôle BOTANIST

    Args:
        current_user: Utilisateur authentifié

    Returns:
        User: L'utilisateur si botaniste

    Raises:
        HTTPException: Si pas botaniste (403)

    Example:
        @router.post("/advice")
        async def create_advice(user: User = Depends(require_botanist)):
    """
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les botanistes peuvent accéder à cette ressource"
        )
    return current_user