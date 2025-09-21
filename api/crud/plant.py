from typing import List
from sqlalchemy.orm import Session
from models.plant import Plant
from schemas.plant import PlantCreate, PlantUpdate
from utils.image_utils import generate_thumbnail
from .base import CRUDBase


class CRUDPlant(CRUDBase[Plant, PlantCreate, PlantUpdate]):
    def create(self, db: Session, *, obj_in: PlantCreate, owner_id: int) -> Plant:
        """Créer une plante avec génération automatique du thumbnail"""
        obj_in_data = obj_in.model_dump()
        obj_in_data["owner_id"] = owner_id

        # Générer le thumbnail si une image est fournie
        if obj_in_data.get("photo_base64"):
            thumbnail = generate_thumbnail(obj_in_data["photo_base64"])
            obj_in_data["photo_thumbnail"] = thumbnail

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Plant, obj_in: PlantUpdate) -> Plant:
        """Mettre à jour une plante avec régénération du thumbnail si nécessaire"""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Régénérer le thumbnail si l'image est modifiée
        if "photo_base64" in update_data and update_data["photo_base64"]:
            thumbnail = generate_thumbnail(update_data["photo_base64"])
            update_data["photo_thumbnail"] = thumbnail

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Plant]:
        """Méthode spécifique pour récupérer les plantes d'un propriétaire"""
        return (
            db.query(self.model)
            .filter(Plant.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


plant = CRUDPlant(Plant)
