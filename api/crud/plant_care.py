from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from models.plant_care import PlantCare, CareStatus
from models.message import ConversationType
from schemas.plant_care import PlantCareCreate, PlantCareUpdate
from crud.message import message


class CRUDPlantCare:
    def create(
        self, db: Session, *, obj_in: PlantCareCreate, owner_id: int
    ) -> PlantCare:
        """Créer une nouvelle demande de garde"""
        db_obj = PlantCare(
            **obj_in.model_dump(), owner_id=owner_id, status=CareStatus.PENDING
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[PlantCare]:
        """Récupérer une garde par son ID avec les relations owner et plant"""
        return (
            db.query(PlantCare)
            .options(joinedload(PlantCare.owner), joinedload(PlantCare.plant))
            .filter(PlantCare.id == id)
            .first()
        )

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        caretaker_id: Optional[int] = None,
        status: Optional[CareStatus] = None
    ) -> List[PlantCare]:
        """Récupérer plusieurs gardes avec filtres optionnels"""
        query = db.query(PlantCare)

        if owner_id is not None:
            query = query.filter(PlantCare.owner_id == owner_id)
        if caretaker_id is not None:
            query = query.filter(PlantCare.caretaker_id == caretaker_id)
        if status is not None:
            query = query.filter(PlantCare.status == status)

        # Trier par updated_at pour les gardiens (dernière prise en premier)
        # Trier par created_at pour les propriétaires (plus récente créée en premier)
        if caretaker_id is not None:
            query = query.order_by(PlantCare.updated_at.desc())
        else:
            query = query.order_by(PlantCare.created_at.desc())

        return query.offset(skip).limit(limit).all()

    def get_available_cares(
        self, db: Session, *, current_user_id: int, skip: int = 0, limit: int = 100
    ) -> List[PlantCare]:
        """Récupérer les gardes disponibles pour l'utilisateur (en attente et créées par d'autres utilisateurs)"""
        return (
            db.query(PlantCare)
            .filter(PlantCare.status == CareStatus.PENDING)
            .filter(PlantCare.owner_id != current_user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(
        self, db: Session, *, db_obj: PlantCare, obj_in: PlantCareUpdate
    ) -> PlantCare:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_status(
        self, db: Session, *, db_obj: PlantCare, status: CareStatus
    ) -> PlantCare:
        """Mettre à jour le statut d'une garde"""
        old_status = db_obj.status
        db_obj.status = status

        if status == CareStatus.ACCEPTED and old_status != CareStatus.ACCEPTED:
            conversation = message.create_conversation(
                db=db,
                participant_ids=[db_obj.owner_id, db_obj.caretaker_id],
                conversation_type=ConversationType.PLANT_CARE,
                related_id=db_obj.id,
                initiator_id=db_obj.caretaker_id,
            )
            db_obj.conversation_id = conversation.id

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj



plant_care = CRUDPlantCare()
