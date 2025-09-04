from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.security import get_current_user
from models.user import User, UserRole
from models.advice import AdvicePriority, ValidationStatus
from crud.advice import advice
from schemas.advice import (
    Advice,
    AdviceCreate,
    AdviceUpdate,
    AdviceValidation,
    AdviceStats,
)
from services.notification_service import NotificationService

router = APIRouter(prefix="/advices", tags=["advices"])

notification_service = NotificationService()


def verify_botanist(current_user: User = Depends(get_current_user)):
    """Vérifier que l'utilisateur est un botaniste"""
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les botanistes peuvent accéder à cette ressource",
        )
    return current_user


@router.get("/stats", response_model=AdviceStats)
async def get_advice_stats(
    db: Session = Depends(get_db), current_user: User = Depends(verify_botanist)
):
    """
    Statistiques personnelles du botaniste

    🔒 **Accès réservé aux botanistes**
    """
    return advice.get_advice_stats(db, current_user.id)


@router.get("/to-review", response_model=List[Dict[str, Any]])
async def get_plant_cares_to_review(
    priority: Optional[AdvicePriority] = Query(
        None, description="Filtrer par priorité"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_botanist),
):
    """
    Gardes à examiner par les botanistes

    🔒 **Accès réservé aux botanistes**
    """
    return advice.get_plant_cares_to_review(
        db=db,
        botanist_id=current_user.id,
        priority_filter=priority,
        skip=skip,
        limit=limit,
    )


@router.get("/reviewed", response_model=List[Dict[str, Any]])
async def get_plant_cares_with_advice(
    validation_status: Optional[ValidationStatus] = Query(
        None, description="Filtrer par statut de validation"
    ),
    my_advice_only: bool = Query(False, description="Afficher seulement mes conseils"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_botanist),
):
    """
    Gardes ayant reçu des avis botaniques

    🔒 **Accès réservé aux botanistes**
    """
    botanist_filter = current_user.id if my_advice_only else None

    return advice.get_plant_cares_with_advice(
        db=db,
        botanist_id=botanist_filter,
        validation_filter=validation_status,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=Advice)
async def create_advice(
    advice_data: AdviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_botanist),
):
    """
    Créer un nouveau conseil botanique

    🔒 **Accès réservé aux botanistes**
    """

    # Vérifier que la garde existe
    from models.plant_care import PlantCare

    plant_care = (
        db.query(PlantCare).filter(PlantCare.id == advice_data.plant_care_id).first()
    )
    if not plant_care:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Garde de plante non trouvée"
        )

    try:
        # Créer le conseil
        new_advice = advice.create_advice(
            db=db, advice_data=advice_data, botanist_id=current_user.id
        )

        # TODO: Réactiver notifications plus tard - temporairement désactivé pour debug
        # await notification_service.send_advice_notification(
        #     db=db,
        #     plant_care_id=advice_data.plant_care_id,
        #     botanist_name=f"{current_user.prenom} {current_user.nom}",
        #     advice_title=advice_data.title,
        #     priority=advice_data.priority
        # )

        return new_advice

    except Exception as e:
        print(f"Erreur création conseil: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du conseil: {str(e)}",
        )


@router.put("/{advice_id}", response_model=Advice)
async def update_advice(
    advice_id: int,
    advice_data: AdviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_botanist),
):
    """
    Modifier un conseil existant (crée une nouvelle version)

    Système de versioning :
    - Crée une nouvelle version du conseil
    - L'ancienne version reste dans l'historique
    - Seule la dernière version est "current"
    - Lien de parenté avec parent_advice_id

    Restrictions :
    - Seul l'auteur du conseil peut le modifier
    - Réinitialise le statut de validation à "pending"

    🔒 **Accès réservé aux botanistes**
    """

    updated_advice = advice.update_advice(
        db=db, advice_id=advice_id, advice_data=advice_data, botanist_id=current_user.id
    )

    if not updated_advice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conseil non trouvé ou vous n'êtes pas autorisé à le modifier",
        )

    try:
        # Notifier le propriétaire de la mise à jour
        await notification_service.send_advice_update_notification(
            db=db,
            advice_id=updated_advice.id,
            botanist_name=f"{current_user.prenom} {current_user.nom}",
        )

        return updated_advice

    except Exception as e:
        # Le conseil a été créé, mais la notification a échoué
        print(f"Notification error: {e}")
        return updated_advice


@router.post("/{advice_id}/validate", response_model=Advice)
async def validate_advice(
    advice_id: int,
    validation_data: AdviceValidation,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_botanist),
):
    """
    Valider ou rejeter le conseil d'un autre botaniste

    Statuts de validation :
    - validated : Conseil approuvé par un pair
    - rejected : Conseil contesté (avec commentaire obligatoire)

    Règles de validation croisée :
    - Un botaniste ne peut pas valider ses propres conseils
    - Seuls les autres botanistes peuvent valider
    - Commentaire obligatoire pour les rejets

    Actions automatiques :
    - Notification à l'auteur du conseil
    - Mise à jour des statistiques du botaniste

    🔒 **Accès réservé aux botanistes**
    """

    validated_advice = advice.validate_advice(
        db=db,
        advice_id=advice_id,
        validation_data=validation_data,
        validator_id=current_user.id,
    )

    if not validated_advice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conseil non trouvé ou vous ne pouvez pas valider vos propres conseils",
        )

    try:
        # Notifier le botaniste auteur de la validation
        await notification_service.send_validation_notification(
            db=db,
            advice_id=advice_id,
            validator_name=f"{current_user.prenom} {current_user.nom}",
            validation_status=validation_data.validation_status,
        )

        return validated_advice

    except Exception as e:
        # La validation a été enregistrée, mais la notification a échoué
        print(f"Validation notification error: {e}")
        return validated_advice


@router.get("/{advice_id}", response_model=Advice)
async def get_advice_by_id(
    advice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_botanist),
):
    """
    Récupérer un conseil par son ID

    🔒 **Accès réservé aux botanistes**
    """

    advice_obj = advice.get_advice_by_id(db, advice_id)
    if not advice_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conseil non trouvé"
        )

    return advice


@router.get("/plant-care/{plant_care_id}", response_model=List[Advice])
async def get_plant_care_advice(
    plant_care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Récupérer les conseils actuels pour une garde (endpoint principal)"""

    # Vérifier que la garde existe
    from models.plant_care import PlantCare

    plant_care_obj = db.query(PlantCare).filter(PlantCare.id == plant_care_id).first()
    if not plant_care_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Garde de plante non trouvée"
        )

    # Vérifier que l'utilisateur a le droit de voir les conseils de cette garde
    # Les conseils sont accessibles à :
    # 1. Tous les botanistes (peuvent voir tous les conseils)
    # 2. Propriétaire et gardien de la garde (peuvent voir les conseils de leur garde)
    # 3. Autres utilisateurs peuvent voir uniquement les conseils validés (publiques)
    
    is_botanist = current_user.role == UserRole.BOTANIST
    is_owner = current_user.id == plant_care_obj.owner_id
    is_caretaker = current_user.id == plant_care_obj.caretaker_id
    
    # Si l'utilisateur n'est ni botaniste, ni propriétaire, ni gardien,
    # on retourne seulement les conseils validés
    if not (is_botanist or is_owner or is_caretaker):
        # Récupérer seulement les conseils validés pour les autres utilisateurs
        from models.advice import ValidationStatus
        return advice.get_current_plant_care_advice(db, plant_care_id, validation_status=ValidationStatus.VALIDATED)
    
    # Pour les botanistes, propriétaires et gardiens : tous les conseils
    return advice.get_current_plant_care_advice(db, plant_care_id)


@router.get("/plant-care/{plant_care_id}/history", response_model=List[Advice])
async def get_plant_care_advice_history(
    plant_care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Récupérer l'historique complet des conseils pour une garde"""

    # Vérifier que la garde existe
    from models.plant_care import PlantCare

    plant_care_obj = db.query(PlantCare).filter(PlantCare.id == plant_care_id).first()
    if not plant_care_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Garde de plante non trouvée"
        )

    # Vérifier que l'utilisateur a le droit de voir les conseils de cette garde
    # (propriétaire, gardien, ou botaniste)
    if (
        current_user.role != UserRole.BOTANIST
        and current_user.id != plant_care_obj.owner_id
        and current_user.id != plant_care_obj.caretaker_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à voir les conseils de cette garde",
        )

    return advice.get_plant_care_advice_history(db, plant_care_id)


@router.get("/plant-care/{plant_care_id}/current", response_model=List[Advice])
async def get_current_plant_care_advice(
    plant_care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Récupérer seulement les conseils actuels (dernière version) pour une garde"""

    # Vérifier que la garde existe
    from models.plant_care import PlantCare

    plant_care_obj = db.query(PlantCare).filter(PlantCare.id == plant_care_id).first()
    if not plant_care_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Garde de plante non trouvée"
        )

    # Vérifier que l'utilisateur a le droit de voir les conseils de cette garde
    # (propriétaire, gardien, ou botaniste)
    if (
        current_user.role != UserRole.BOTANIST
        and current_user.id != plant_care_obj.owner_id
        and current_user.id != plant_care_obj.caretaker_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à voir les conseils de cette garde",
        )

    return advice.get_current_plant_care_advice(db, plant_care_id)


@router.get("/priority/{priority}/count")
async def get_count_by_priority(
    priority: AdvicePriority,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_botanist),
):
    """
    Obtenir le nombre de gardes par priorité

    🔒 **Accès réservé aux botanistes**
    """
    from models.advice import Advice
    from sqlalchemy import and_

    count = (
        db.query(Advice)
        .filter(and_(Advice.is_current_version, Advice.priority == priority))
        .count()
    )

    return {"priority": priority, "count": count}
