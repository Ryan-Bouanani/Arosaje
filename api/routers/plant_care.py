from typing import List, Optional
import logging
import datetime as dt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from utils.database import get_db
from utils.security import get_current_user
from crud.plant_care import plant_care
from crud.plant import plant as plant_crud
from crud.user import user as user_crud
from models.plant_care import CareStatus, PlantCare as PlantCareModel
from models.user import User as UserModel
from schemas.plant_care import PlantCare, PlantCareCreate, PlantCareInDB
from schemas.user import User
from crud.message import message
from models.message import ConversationType
from services.geocoding_service import geocoding_service

router = APIRouter(prefix="/plant-care", tags=["plant-care"])


@router.post("/", response_model=PlantCare)
async def create_plant_care(
    *,
    db: Session = Depends(get_db),
    plant_care_in: PlantCareCreate,
    current_user: User = Depends(get_current_user),
):
    """Créer une demande de garde de plante"""
    try:
        logging.info(
            f"Tentative de création d'une garde pour la plante {plant_care_in.plant_id}"
        )

        # Vérifier que la plante existe
        plant = plant_crud.get(db, id=plant_care_in.plant_id)
        if not plant:
            logging.error(f"Plante {plant_care_in.plant_id} non trouvée")
            raise HTTPException(status_code=404, detail="Plante non trouvée")

        # Vérifier que l'utilisateur est bien le propriétaire de la plante
        if plant.owner_id != current_user.id:
            logging.error(
                f"L'utilisateur {current_user.id} n'est pas le propriétaire de la plante {plant_care_in.plant_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="Vous n'êtes pas le propriétaire de cette plante",
            )

        # Vérifier que le gardien existe si un gardien est spécifié
        if plant_care_in.caretaker_id is not None:
            caretaker = (
                db.query(UserModel)
                .filter(UserModel.id == plant_care_in.caretaker_id)
                .first()
            )
            if not caretaker:
                logging.error(f"Gardien {plant_care_in.caretaker_id} non trouvé")
                raise HTTPException(status_code=404, detail="Gardien non trouvé")

        # Géocoder l'adresse si fournie
        if plant_care_in.localisation:
            logging.info(f"Géocodage de l'adresse: {plant_care_in.localisation}")
            coords = await geocoding_service.geocode_address(plant_care_in.localisation)
            if coords:
                plant_care_in.latitude = coords[0]
                plant_care_in.longitude = coords[1]
                logging.info(f"Coordonnées obtenues: {coords}")
            else:
                logging.warning(
                    f"Impossible de géocoder l'adresse: {plant_care_in.localisation}"
                )

        logging.info("Création de la garde...")
        result = plant_care.create(db, obj_in=plant_care_in, owner_id=current_user.id)
        logging.info(f"Garde créée avec succès: {result.id}")
        return result
    except ValueError as e:
        logging.error(f"Erreur de validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Erreur lors de la création de la garde: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la création de la garde: {str(e)}"
        )


@router.get("/", response_model=List[PlantCare])
def read_plant_cares(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[CareStatus] = None,
    as_owner: Optional[bool] = None,
    as_caretaker: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
):
    """Lister les gardes de plantes avec filtres"""
    if as_owner is True:
        return plant_care.get_multi(
            db, skip=skip, limit=limit, owner_id=current_user.id, status=status
        )
    elif as_caretaker is True:
        return plant_care.get_multi(
            db, skip=skip, limit=limit, caretaker_id=current_user.id, status=status
        )
    elif as_owner is False:
        # Récupérer les gardes disponibles (en attente et créées par d'autres utilisateurs)
        return plant_care.get_available_cares(
            db, current_user_id=current_user.id, skip=skip, limit=limit
        )
    else:
        # Par défaut, retourner une liste vide
        return []


@router.get("/{care_id}", response_model=PlantCareInDB)
def get_plant_care(
    care_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Récupérer les détails complets d'une garde spécifique"""
    db_care = plant_care.get(db=db, id=care_id)
    if db_care is None:
        raise HTTPException(status_code=404, detail="Garde non trouvée")
    return db_care


@router.put("/{care_id}/cancel", response_model=PlantCare)
async def cancel_plant_care(
    care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Annuler une garde (propriétaire ou gardien)"""
    db_care = plant_care.get(db, id=care_id)
    if not db_care:
        raise HTTPException(status_code=404, detail="Garde non trouvée")

    # Vérifier les permissions
    is_owner = db_care.owner_id == current_user.id
    is_caretaker = db_care.caretaker_id == current_user.id

    if not (is_owner or is_caretaker):
        raise HTTPException(
            status_code=403,
            detail="Seul le propriétaire ou le gardien peut annuler cette garde",
        )

    # Vérifier que la garde peut être annulée
    if db_care.status in [CareStatus.COMPLETED, CareStatus.CANCELLED]:
        raise HTTPException(
            status_code=400, detail="Cette garde ne peut plus être annulée"
        )

    # Mettre à jour le statut
    return plant_care.update_status(db, db_obj=db_care, status=CareStatus.CANCELLED)


@router.put("/{care_id}/start", response_model=PlantCare)
async def start_plant_care(
    care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Démarrer une garde manuellement (gardien)"""
    db_care = plant_care.get(db, id=care_id)
    if not db_care:
        raise HTTPException(status_code=404, detail="Garde non trouvée")

    if db_care.status != CareStatus.ACCEPTED:
        raise HTTPException(
            status_code=400, detail="La garde doit être acceptée pour être démarrée"
        )

    if db_care.caretaker_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Seul le gardien peut démarrer cette garde"
        )

    # Mettre à jour le statut
    return plant_care.update_status(db, db_obj=db_care, status=CareStatus.IN_PROGRESS)


@router.put("/{care_id}/accept", response_model=PlantCare)
async def accept_plant_care(
    care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accepter une garde de plante (gardien)"""
    db_care = plant_care.get(db=db, id=care_id)
    if db_care is None:
        raise HTTPException(status_code=404, detail="Garde non trouvée")

    if db_care.status != CareStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cette garde n'est plus disponible")

    if db_care.owner_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Vous ne pouvez pas accepter votre propre garde"
        )

    # Créer une conversation
    conversation = message.create_conversation(
        db=db,
        participant_ids=[db_care.owner_id, current_user.id],
        conversation_type=ConversationType.PLANT_CARE,
        related_id=care_id,
        initiator_id=current_user.id,
    )

    # Mettre à jour la garde
    db_care.status = CareStatus.ACCEPTED
    db_care.caretaker_id = current_user.id
    db_care.conversation_id = conversation.id
    db.add(db_care)
    db.commit()
    db.refresh(db_care)

    # Notifications email désactivées temporairement
    print(f"Garde {care_id} acceptée par {current_user.get_full_name()}")

    return db_care


@router.put("/{care_id}/complete", response_model=PlantCare)
async def complete_plant_care_by_owner(
    care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Terminer une garde manuellement"""
    db_care = plant_care.get(db, id=care_id)
    if not db_care:
        raise HTTPException(status_code=404, detail="Garde non trouvée")

    # Vérifier que l'utilisateur est le propriétaire de la garde
    if db_care.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Seul le propriétaire peut terminer cette garde"
        )

    # Vérifier que la garde peut être terminée ou annulée
    if db_care.status not in [
        CareStatus.PENDING,
        CareStatus.ACCEPTED,
        CareStatus.IN_PROGRESS,
    ]:
        raise HTTPException(
            status_code=400,
            detail="Seules les gardes en attente, acceptées ou en cours peuvent être terminées",
        )

    # Déterminer le nouveau statut selon le statut actuel
    if db_care.status == CareStatus.PENDING:
        # Annulation d'une demande en attente
        new_status = CareStatus.CANCELLED
    else:
        # Terminaison d'une garde acceptée ou en cours
        new_status = CareStatus.COMPLETED

    # Mettre à jour la garde
    db_care = plant_care.update_status(db, db_obj=db_care, status=new_status)

    # Envoyer une notification au gardien si il y en a un
    if db_care.caretaker_id:
        caretaker = user_crud.get(db, id=db_care.caretaker_id)

        # Email de notification (temporairement désactivé)
        # email_service = EmailService()
        # try:
        #     await email_service.send_care_completed_by_owner_notification(
        #         caretaker_email=caretaker.email,
        #         caretaker_name=caretaker.get_full_name(),
        #         owner_name=current_user.get_full_name(),
        #         plant_name=plant.nom,
        #     )
        # except Exception as e:
        #     print(f"Erreur envoi email: {e}")
        print(
            f"Email de notification désactivé temporairement - Gardien: {caretaker.get_full_name()}"
        )

    return db_care


@router.get("/by-plant/{plant_id}", response_model=PlantCareInDB)
def get_plant_care_by_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Récupérer une garde par l'ID de la plante"""

    # Vérifier que la plante existe
    plant = plant_crud.get(db, id=plant_id)

    # Si la plante n'existe pas, créer une plante fictive pour la démonstration
    if not plant:
        # Créer une plante fictive basée sur l'ID pour la démonstration
        fake_plants = {
            1: {"nom": "Monstera Deliciosa", "espece": "Monstera"},
            2: {"nom": "Ficus Lyrata", "espece": "Ficus"},
            3: {"nom": "Calathea Orbifolia", "espece": "Calathea"},
            4: {"nom": "Pilea Peperomioides", "espece": "Pilea"},
        }

        if plant_id in fake_plants:
            fake_plant_data = fake_plants[plant_id]

            # Retourner une garde fictive pour la plante de démonstration
            fake_care_data = {
                "id": 0,
                "plant_id": plant_id,
                "owner_id": current_user.id,
                "caretaker_id": None,
                "start_date": dt.datetime.now(),
                "end_date": dt.datetime.now(),
                "status": "pending",
                "care_instructions": f'Cette {fake_plant_data["nom"]} est disponible pour la garde',
                "localisation": "Plante de démonstration - Paris",
                "start_photo_url": None,
                "end_photo_url": None,
                "conversation_id": None,
                "created_at": dt.datetime.now(),
                "updated_at": dt.datetime.now(),
                "plant": {
                    "id": plant_id,
                    "nom": fake_plant_data["nom"],
                    "espece": fake_plant_data["espece"],
                    "photo": None,
                },
                "owner": {
                    "id": current_user.id,
                    "nom": current_user.nom,
                    "prenom": current_user.prenom,
                    "email": current_user.email,
                },
            }
            return fake_care_data
        else:
            raise HTTPException(status_code=404, detail="Plante non trouvée")

    # Vérifier que l'utilisateur a le droit de voir cette plante (seulement pour les vraies plantes)
    if plant.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Vous n'avez pas accès à cette plante"
        )

    # Récupérer la garde la plus récente pour cette plante avec les relations
    db_care = (
        db.query(PlantCareModel)
        .options(joinedload(PlantCareModel.owner), joinedload(PlantCareModel.plant))
        .filter(PlantCareModel.plant_id == plant_id)
        .order_by(PlantCareModel.created_at.desc())
        .first()
    )

    # Si aucune garde n'existe, créer une structure de garde fictive pour afficher les détails de la plante
    if db_care is None:
        from datetime import datetime

        # Récupérer les informations du propriétaire
        owner = user_crud.get(db, id=plant.owner_id)

        # Créer une garde fictive pour pouvoir afficher les détails de la plante
        fake_care_data = {
            "id": 0,  # ID fictif
            "plant_id": plant_id,
            "owner_id": plant.owner_id,
            "caretaker_id": None,
            "start_date": datetime.now(),
            "end_date": datetime.now(),
            "status": "pending",
            "care_instructions": "Aucune garde active pour cette plante",
            "localisation": "Emplacement de la plante non spécifié",
            "start_photo_url": None,
            "end_photo_url": None,
            "conversation_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "plant": {
                "id": plant.id,
                "nom": plant.nom,
                "espece": plant.espece,
                "photo": plant.photo,
            },
            "owner": (
                {
                    "id": owner.id,
                    "nom": owner.nom,
                    "prenom": owner.prenom,
                    "email": owner.email,
                }
                if owner
                else None
            ),
        }

        # Retourner les données directement au format attendu
        return fake_care_data

    return db_care
