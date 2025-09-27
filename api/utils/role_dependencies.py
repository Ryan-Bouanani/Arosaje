"""
Dependencies génériques pour la vérification des rôles utilisateur
Centralise toute la logique de sécurité basée sur les rôles
"""
from typing import List
from fastapi import Depends, HTTPException, status
from models.user import User, UserRole
from utils.security import get_current_user


def require_role(required_role: UserRole):
    """
    Factory générique pour créer des dependencies de vérification de rôle

    Args:
        required_role: Le rôle requis pour accéder à l'endpoint

    Returns:
        Function: Dependency function pour FastAPI

    Example:
        @router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès réservé aux {required_role.value}s"
            )
        return current_user

    role_checker.__name__ = f"require_{required_role.value}"
    return role_checker


def require_roles(required_roles: List[UserRole]):
    """
    Factory pour créer des dependencies acceptant plusieurs rôles

    Args:
        required_roles: Liste des rôles acceptés

    Returns:
        Function: Dependency function pour FastAPI

    Example:
        @router.get("/botanist-or-admin", dependencies=[Depends(require_roles([UserRole.BOTANIST, UserRole.ADMIN]))])
    """
    def roles_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            roles_str = ", ".join([role.value for role in required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès réservé aux rôles : {roles_str}"
            )
        return current_user

    roles_checker.__name__ = f"require_roles_{len(required_roles)}"
    return roles_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Shortcut pour vérifier les droits administrateur
    Remplace les anciennes fonctions check_admin_rights()

    Example:
        @router.get("/admin/stats", dependencies=[Depends(require_admin)])
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user


def require_botanist(current_user: User = Depends(get_current_user)) -> User:
    """
    Shortcut pour vérifier les droits botaniste
    Remplace les anciennes fonctions verify_botanist()

    Example:
        @router.get("/advices/stats", dependencies=[Depends(require_botanist)])
    """
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les botanistes peuvent accéder à cette ressource"
        )
    return current_user


def require_user_or_botanist(current_user: User = Depends(get_current_user)) -> User:
    """
    Permet l'accès aux utilisateurs standards ET aux botanistes
    Exclus les admins (qui ont leurs propres endpoints)

    Example:
        @router.get("/my-plants", dependencies=[Depends(require_user_or_botanist)])
    """
    allowed_roles = [UserRole.USER, UserRole.BOTANIST]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux utilisateurs et botanistes"
        )
    return current_user


def require_botanist_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Permet l'accès aux botanistes ET aux admins
    Utile pour les endpoints de supervision/modération

    Example:
        @router.get("/reports/moderate", dependencies=[Depends(require_botanist_or_admin)])
    """
    allowed_roles = [UserRole.BOTANIST, UserRole.ADMIN]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux botanistes et administrateurs"
        )
    return current_user


def get_current_user_with_role_check(minimum_role: UserRole = UserRole.USER):
    """
    Retourne l'utilisateur courant après vérification du rôle minimum
    Utile quand on veut à la fois l'utilisateur ET vérifier son rôle

    Args:
        minimum_role: Rôle minimum requis (hiérarchie: USER < BOTANIST < ADMIN)

    Example:
        def my_endpoint(user: User = Depends(get_current_user_with_role_check(UserRole.BOTANIST))):
    """
    def user_with_role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Hiérarchie simple : USER=1, BOTANIST=2, ADMIN=3
        role_hierarchy = {
            UserRole.USER: 1,
            UserRole.BOTANIST: 2,
            UserRole.ADMIN: 3
        }

        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(minimum_role, 999)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Niveau d'accès insuffisant. Rôle {minimum_role.value} requis."
            )
        return current_user

    return user_with_role_checker