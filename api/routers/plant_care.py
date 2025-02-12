from typing import List
import logging
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status, Query
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.security import get_current_user
from utils.image_handler import ImageHandler
from crud.plant_care import plant_care
from crud.plant import plant as plant_crud
from models.plant_care import CareStatus
from models.user import User as UserModel
from schemas.plant_care import PlantCare, PlantCareCreate, PlantCareUpdate
from schemas.user import User
from crud.message import message
from models.message import ConversationType
from schemas.message import MessageCreate

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
        
        # Vérifier que le gardien existe
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
        return plant_care.get_multi(db, skip=skip, limit=limit, caretaker_id=current_user.id, status=status)
    return plant_care.get_multi(db, skip=skip, limit=limit, status=status)

@router.get("/{care_id}", response_model=PlantCare)
def read_plant_care(
    care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les détails d'une garde"""
    db_care = plant_care.get(db, id=care_id)
    if not db_care:
        raise HTTPException(status_code=404, detail="Garde non trouvée")
    return db_care

@router.put("/{care_id}/status")
async def update_care_status(
    care_id: int,
    status: str = Query(..., regex="^(accepted|rejected)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        print(f"Mise à jour du statut de garde {care_id} à {status} par l'utilisateur {current_user.id}")
        
        # Récupérer la demande de garde
        db_care = plant_care.get(db, id=care_id)
        if not db_care:
            raise HTTPException(status_code=404, detail="Demande de garde non trouvée")
            
        # Vérifier que l'utilisateur est bien le gardien
        if db_care.caretaker_id != current_user.id:
            raise HTTPException(status_code=403, detail="Seul le gardien peut accepter ou refuser la demande")
            
        # Mettre à jour le statut
        db_care = plant_care.update_status(db, db_obj=db_care, status=status)
        print(f"Statut de garde mis à jour avec succès")
        
        # Créer une conversation si la demande est acceptée
        if status == "accepted":
            print(f"Création d'une conversation pour la garde {care_id}")
            conversation = message.create_conversation(
                db=db,
                participant_ids=[db_care.owner_id, db_care.caretaker_id],
                conversation_type=ConversationType.PLANT_CARE,
                related_id=care_id
            )
            print(f"Conversation créée avec l'ID {conversation.id}")
            
            # Créer un message automatique
            message_content = "La demande de garde a été acceptée"
            print(f"Création du message automatique: {message_content}")
            
            new_message = message.create_message(
                db=db,
                message=MessageCreate(
                    conversation_id=conversation.id,
                    content=message_content
                ),
                sender_id=None  # Message automatique, pas d'expéditeur
            )
            print(f"Message automatique créé avec l'ID {new_message.id}")
            
            # Mettre à jour l'ID de la conversation dans la garde
            db_care.conversation_id = conversation.id
            db.add(db_care)
            
            # Commit explicite pour s'assurer que tout est sauvegardé
            db.commit()
            
            return {
                "status": "success",
                "care_status": status,
                "conversation_id": conversation.id
            }
            
        return {"status": "success", "care_status": status}
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du statut: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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