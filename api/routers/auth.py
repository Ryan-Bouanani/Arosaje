from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from utils.database import get_db
from utils.security import (
    verify_password,
    create_access_token,
    get_current_user,
    get_password_hash
)
from crud.user import user as user_crud
from schemas.token import Token
from schemas.user import UserCreate, User, UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login avec OAuth2 form"""
    user = user_crud.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.mot_de_passe):
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
    
    # Hasher le mot de passe
    hashed_password = get_password_hash(user_in.mot_de_passe)
    user_in.mot_de_passe = hashed_password
    
    # Créer l'utilisateur
    user = user_crud.create(db, obj_in=user_in)
    return user

@router.get("/me", response_model=User)
async def read_users_me(
    current_user = Depends(get_current_user)
):
    """Renvoie les informations de l'utilisateur connecté"""
    return current_user 