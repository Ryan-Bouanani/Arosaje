from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from utils.database import get_db
from utils.security import get_current_user
from models.user import User, UserRole
from schemas.user import User as UserSchema
from crud.user import user as user_crud
from services.email.email_service import EmailService
from models.plant_care import PlantCare
from models.plant_care_advice import PlantCareAdvice

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
    """Lister tous les comptes en attente de vérification"""
    return db.query(User).filter(User.is_verified == False).all()

@router.post("/verify/{user_id}")
async def verify_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_rights)
):
    """Vérifier un compte utilisateur"""
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
    """Rejeter et supprimer un compte utilisateur"""
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

@router.get("/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_rights)
):
    """Statistiques pour le dashboard administrateur"""
    try:
        # Compter les utilisateurs
        total_users = db.query(User).count()
        pending_users = db.query(User).filter(User.is_verified == False).count()
        
        # Compter les gardes actives (statuts IN_PROGRESS et ACCEPTED)
        active_cares = db.query(PlantCare).filter(
            PlantCare.status.in_(['IN_PROGRESS', 'ACCEPTED'])
        ).count()
        
        # Compter les conseils donnés
        total_advices = db.query(PlantCareAdvice).count()
        
        return {
            "total_users": total_users,
            "pending_users": pending_users,
            "active_cares": active_cares,
            "total_advices": total_advices
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

@router.get("/verified-users", response_model=List[UserSchema])
async def get_verified_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_rights)
):
    """Lister tous les utilisateurs vérifiés et actifs"""
    return db.query(User).filter(User.is_verified == True).all()

@router.put("/change-role/{user_id}")
async def change_user_role(
    user_id: int,
    role_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_rights)
):
    """Modifier le rôle d'un utilisateur"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Valider le nouveau rôle
    new_role = role_data.get('role', '').upper()
    valid_roles = ['USER', 'BOTANIST', 'ADMIN']
    
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rôle invalide. Rôles valides: {valid_roles}"
        )
    
    # Convertir en UserRole enum
    try:
        user_role = UserRole(new_role.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rôle invalide: {new_role}"
        )
    
    # Éviter qu'un admin change son propre rôle
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas changer votre propre rôle"
        )
    
    # Mettre à jour le rôle
    user.role = user_role
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"Rôle de l'utilisateur {user.prenom} {user.nom} changé vers {new_role}",
        "user": {
            "id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email,
            "role": user.role.value
        }
    } 