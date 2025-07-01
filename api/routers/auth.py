from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from utils.database import get_db
from utils.security import create_access_token, get_current_user
from utils.password import verify_password, get_password_hash
from crud.user import user as user_crud
from schemas.token import Token
from schemas.user import UserCreate, User, UserRoleUpdate
from models.user import UserRole
from services.email.email_service import EmailService
from services.monitoring_service import monitoring_service
from services.analytics_service import analytics_service
from utils.platform import detect_platform

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# Initialisation du service d'email
email_service = EmailService()

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """Login avec OAuth2 form"""
    user = user_crud.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier si le compte est vérifié (sauf pour l'admin)
    if user.role != UserRole.ADMIN and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte est en attente de vérification par un administrateur"
        )
    
    # Détecter la plateforme
    platform = detect_platform(request)
    
    # Mettre à jour la métrique des utilisateurs actifs
    monitoring_service.increment_active_users(platform=platform)
    
    # Tracker l'utilisation de la fonctionnalité de login
    await analytics_service.track_feature_usage(
        feature="login",
        platform=platform,
        user_id=str(user.id)
    )
    
    # Tracker la localisation si disponible
    if "x-forwarded-for" in request.headers:
        # Note: Dans un environnement de production, il faudrait utiliser un service de géolocalisation
        await analytics_service.track_geographic_usage(
            country_code="FR",  # Par défaut pour le moment
            platform=platform,
            user_id=str(user.id)
        )
    
    # Envoyer un événement d'usage vers InfluxDB
    await monitoring_service.send_usage_event_to_influxdb(
        event_type="user_login",
        user_id=str(user.id),
        platform=platform,
        properties={"user_role": user.role.value if user.role else "unknown"}
    )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=User)
async def register(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Inscription d'un nouvel utilisateur"""
    if user_crud.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Création de l'utilisateur
    user = user_crud.create(db, obj_in=user_in)
    
    # Détecter la plateforme
    platform = detect_platform(request)
    
    # Tracker l'utilisation de la fonctionnalité d'inscription
    await analytics_service.track_feature_usage(
        feature="register",
        platform=platform,
        user_id=str(user.id)
    )
    
    # Envoi de l'email de bienvenue
    try:
        await email_service.send_welcome_email(
            recipient_email=user.email,
            user_name=f"{user.prenom} {user.nom}"
        )
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de bienvenue: {e}")
    
    return user

@router.get("/me", response_model=User)
async def read_users_me(
    request: Request,
    current_user = Depends(get_current_user)
):
    """Renvoie les informations de l'utilisateur connecté"""
    # Détecter la plateforme
    platform = detect_platform(request)
    
    # Tracker l'utilisation de la fonctionnalité de profil
    await analytics_service.track_feature_usage(
        feature="view_profile",
        platform=platform,
        user_id=str(current_user.id)
    )
    return current_user

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Logout de l'utilisateur"""
    # Détecter la plateforme
    platform = detect_platform(request)
    
    # Décrémenter la métrique des utilisateurs actifs
    monitoring_service.decrement_active_users(platform=platform)
    
    # Tracker l'utilisation de la fonctionnalité de déconnexion
    await analytics_service.track_feature_usage(
        feature="logout",
        platform=platform,
        user_id=str(current_user.id)
    )
    
    # Envoyer un événement d'usage vers InfluxDB
    await monitoring_service.send_usage_event_to_influxdb(
        event_type="user_logout",
        user_id=str(current_user.id),
        platform=platform
    )
    
    return {"message": "Déconnexion réussie"}

@router.put("/users/{user_id}/role", response_model=User)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Mettre à jour le rôle d'un utilisateur"""
    # Vérifier que l'utilisateur existe
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Pour l'instant, on permet à l'utilisateur de modifier son propre rôle
    # Dans un environnement de production, il faudrait ajouter une vérification d'admin
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas modifier le rôle d'un autre utilisateur"
        )
    
    # Détecter la plateforme
    platform = detect_platform(request)
    
    # Tracker l'utilisation de la fonctionnalité de mise à jour du rôle
    await analytics_service.track_feature_usage(
        feature="update_role",
        platform=platform,
        user_id=str(current_user.id)
    )
    
    # Mettre à jour le rôle
    return user_crud.update_role(db, db_obj=user, role=role_update.role) 