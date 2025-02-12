from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# Initialisation du service d'email
email_service = EmailService()

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login avec OAuth2 form"""
    user = user_crud.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=User)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """Inscription d'un nouvel utilisateur"""
    if user_crud.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Création de l'utilisateur
    user = user_crud.create(db, obj_in=user_in)
    
    # Envoi de l'email de bienvenue
    try:
        await email_service.send_welcome_email(
            recipient_email=user.email,
            user_name=f"{user.prenom} {user.nom}"
        )
    except Exception as e:
        # Log l'erreur mais ne pas bloquer l'inscription
        print(f"Erreur lors de l'envoi de l'email de bienvenue: {e}")
    
    return user

@router.get("/me", response_model=User)
async def read_users_me(
    current_user = Depends(get_current_user)
):
    """Renvoie les informations de l'utilisateur connecté"""
    return current_user

@router.put("/users/{user_id}/role", response_model=User)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
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
    
    # Mettre à jour le rôle
    return user_crud.update_role(db, db_obj=user, role=role_update.role) 