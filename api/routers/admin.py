from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from utils.database import get_db
from utils.security import get_current_user
from models.user import User, UserRole
from schemas.user import User as UserSchema
from crud.user import user as user_crud
from services.email.email_service import EmailService

router = APIRouter(
    prefix="/admin",
    tags=["administration"]
)

# Initialisation du service d'email
email_service = EmailService()

def check_admin_rights(current_user: dict = Depends(get_current_user)):
    """Vérifie que l'utilisateur est un admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user

async def send_validation_email(user_email: str, user_name: str):
    """Envoie l'email de validation en arrière-plan"""
    try:
        await email_service.send_account_validated_email(
            recipient_email=user_email,
            user_name=user_name
        )
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de validation: {e}")

async def send_rejection_email(user_email: str, user_name: str):
    """Envoie l'email de rejet en arrière-plan"""
    try:
        await email_service.send_account_rejected_email(
            recipient_email=user_email,
            user_name=user_name
        )
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de rejet: {e}")

@router.get("/pending-verifications", response_model=List[UserSchema])
async def get_pending_verifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_rights)
):
    """Liste tous les comptes en attente de vérification"""
    return db.query(User).filter(User.is_verified == False).all()

@router.post("/verify/{user_id}")
async def verify_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_rights)
):
    """Vérifie un compte utilisateur"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)

    # Envoyer l'email en arrière-plan
    background_tasks.add_task(
        send_validation_email,
        user_email=user.email,
        user_name=f"{user.prenom} {user.nom}"
    )

    return {"message": "Compte vérifié avec succès"}

@router.post("/reject/{user_id}")
async def reject_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_rights)
):
    """Rejette un compte utilisateur"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Sauvegarder les informations de l'utilisateur avant suppression
    user_email = user.email
    user_name = f"{user.prenom} {user.nom}"
    
    # Supprimer l'utilisateur
    db.delete(user)
    db.commit()

    # Envoyer l'email en arrière-plan
    background_tasks.add_task(
        send_rejection_email,
        user_email=user_email,
        user_name=user_name
    )

    return {"message": "Compte rejeté et supprimé avec succès"} 