from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status, Query
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.security import get_current_user
from utils.image_handler import ImageHandler
from crud.plant_care import plant_care
from crud.plant import plant as plant_crud
from crud.user import user as user_crud
from models.plant_care import CareStatus
from models.user import User as UserModel
from schemas.plant_care import PlantCare, PlantCareCreate, PlantCareUpdate, PlantCareInDB
from schemas.user import User
from crud.message import message
from models.message import ConversationType
from schemas.message import MessageCreate
from services.email.email_service import EmailService

router = APIRouter(
    prefix="/plant-care",
    tags=["plant-care"]
)

@router.post("/", response_model=PlantCare)
async def create_plant_care(
    *,
    db: Session = Depends(get_db),
    plant_care_in: PlantCareCreate,
    current_user: User = Depends(get_current_user)
):
    """Créer une demande de garde de plante"""
    try:
        logging.info(f"Tentative de création d'une garde pour la plante {plant_care_in.plant_id}")
        
        # Vérifier que la plante existe
        plant = plant_crud.get(db, id=plant_care_in.plant_id)
        if not plant:
            logging.error(f"Plante {plant_care_in.plant_id} non trouvée")
            raise HTTPException(status_code=404, detail="Plante non trouvée")
        
        # Vérifier que l'utilisateur est bien le propriétaire de la plante
        if plant.owner_id != current_user.id:
            logging.error(f"L'utilisateur {current_user.id} n'est pas le propriétaire de la plante {plant_care_in.plant_id}")
            raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire de cette plante")
        
        # Vérifier que le gardien existe si un gardien est spécifié
        if plant_care_in.caretaker_id is not None:
            caretaker = db.query(UserModel).filter(UserModel.id == plant_care_in.caretaker_id).first()
            if not caretaker:
                logging.error(f"Gardien {plant_care_in.caretaker_id} non trouvé")
                raise HTTPException(status_code=404, detail="Gardien non trouvé")
        
        logging.info("Création de la garde...")
        result = plant_care.create(db, obj_in=plant_care_in, owner_id=current_user.id)
        logging.info(f"Garde créée avec succès: {result.id}")
        return result
    except ValueError as e:
        logging.error(f"Erreur de validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Erreur lors de la création de la garde: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la garde: {str(e)}")

@router.get("/", response_model=List[PlantCare])
def read_plant_cares(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: CareStatus = None,
    as_owner: bool = None,
    current_user: User = Depends(get_current_user)
):
    """Liste les gardes de plantes"""
    if as_owner is True:
        return plant_care.get_multi(db, skip=skip, limit=limit, owner_id=current_user.id, status=status)
    elif as_owner is False:
        # Récupérer les gardes disponibles (en attente et créées par d'autres utilisateurs)
        return plant_care.get_available_cares(db, current_user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{care_id}", response_model=PlantCareInDB)
def get_plant_care(
    care_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Récupère les détails d'une garde spécifique"""
    db_care = plant_care.get(db=db, id=care_id)
    if db_care is None:
        raise HTTPException(status_code=404, detail="Garde non trouvée")
    return db_care

@router.put("/{care_id}/status", response_model=PlantCareInDB)
async def update_plant_care_status(
    care_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Accepte une garde"""
    db_care = plant_care.get(db=db, id=care_id)
    if db_care is None:
        raise HTTPException(status_code=404, detail="Garde non trouvée")
    
    if db_care.status != "pending":
        raise HTTPException(status_code=400, detail="Cette garde n'est plus disponible")
    
    if db_care.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas accepter votre propre garde")
    
    # Créer une conversation
    conversation = message.create_conversation(
        db=db,
        participant_ids=[db_care.owner_id, current_user.id],
        conversation_type=ConversationType.PLANT_CARE,
        related_id=care_id,
        initiator_id=current_user.id
    )

    # Mettre à jour la garde directement
    db_care.status = CareStatus.ACCEPTED
    db_care.caretaker_id = current_user.id
    db_care.conversation_id = conversation.id
    db.add(db_care)
    db.commit()
    db.refresh(db_care)

    # Récupérer les informations nécessaires pour l'email
    owner = user_crud.get(db, id=db_care.owner_id)
    caretaker = user_crud.get(db, id=current_user.id)
    plant = plant_crud.get(db, id=db_care.plant_id)

    # Envoyer l'email de notification
    email_service = EmailService()
    await email_service.send_care_accepted_notification(
        owner_email=owner.email,
        owner_name=owner.get_full_name(),
        caretaker_name=caretaker.get_full_name(),
        plant_name=plant.nom,
        start_date=db_care.start_date.strftime("%d/%m/%Y"),
        end_date=db_care.end_date.strftime("%d/%m/%Y"),
        location=db_care.localisation,
        conversation_id=str(conversation.id)
    )

    return db_care

@router.post("/{care_id}/photos/start", response_model=PlantCare)
async def upload_start_photo(
    care_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload la photo de début de garde"""
    db_care = plant_care.get(db, id=care_id)
    if not db_care:
        raise HTTPException(status_code=404, detail="Garde non trouvée")
    
    if db_care.status != CareStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="La garde doit être acceptée")
    
    if db_care.caretaker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le gardien peut uploader la photo de début")
    
    # Vérifier si l'image est valide
    if not ImageHandler.is_valid_image(photo):
        raise HTTPException(
            status_code=400,
            detail="Format d'image non supporté. Utilisez JPG, JPEG, PNG ou GIF"
        )
    
    # Sauvegarder l'image
    _, photo_url = await ImageHandler.save_image(photo, f"plant_care_start_{care_id}")
    db_care = plant_care.add_photo(db, db_obj=db_care, photo_url=photo_url)
    
    # Mettre à jour le statut
    return plant_care.update_status(db, db_obj=db_care, status=CareStatus.IN_PROGRESS)

@router.post("/{care_id}/photos/end", response_model=PlantCare)
async def upload_end_photo(
    care_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload la photo de fin de garde"""
    db_care = plant_care.get(db, id=care_id)
    if not db_care:
        raise HTTPException(status_code=404, detail="Garde non trouvée")
    
    if db_care.status != CareStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="La garde doit être en cours")
    
    if db_care.caretaker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le gardien peut uploader la photo de fin")
    
    # Vérifier si l'image est valide
    if not ImageHandler.is_valid_image(photo):
        raise HTTPException(
            status_code=400,
            detail="Format d'image non supporté. Utilisez JPG, JPEG, PNG ou GIF"
        )
    
    # Sauvegarder l'image
    _, photo_url = await ImageHandler.save_image(photo, f"plant_care_end_{care_id}")
    db_care = plant_care.add_photo(db, db_obj=db_care, photo_url=photo_url, is_end_photo=True)
    
    # Mettre à jour le statut
    return plant_care.update_status(db, db_obj=db_care, status=CareStatus.COMPLETED)

@router.get("/by-plant/{plant_id}", response_model=PlantCareInDB)
def get_plant_care_by_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les détails d'une garde par l'ID de la plante"""
    # Récupérer la garde la plus récente pour cette plante
    db_care = (
        db.query(PlantCare)
        .filter(PlantCare.plant_id == plant_id)
        .order_by(PlantCare.created_at.desc())
        .first()
    )
    
    if db_care is None:
        raise HTTPException(status_code=404, detail="Aucune garde trouvée pour cette plante")
        
    return db_care