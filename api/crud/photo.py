from typing import List, Optional
from sqlalchemy.orm import Session
from models.photo import Photo
from schemas.photo import PhotoCreate
from .base import CRUDBase
from utils.image_handler import ImageHandler

class CRUDPhoto(CRUDBase[Photo, PhotoCreate, PhotoCreate]):
    def get_by_plant(
        self, 
        db: Session, 
        *, 
        plant_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Photo]:
        """Récupère toutes les photos d'une plante"""
        return (
            db.query(self.model)
            .filter(Photo.plant_id == plant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(
        self,
        db: Session,
        *,
        plant_id: int,
        type: str
    ) -> Optional[Photo]:
        """Récupère une photo spécifique d'une plante par type"""
        return (
            db.query(self.model)
            .filter(Photo.plant_id == plant_id, Photo.type == type)
            .first()
        )

    def delete_with_file(self, db: Session, *, id: int) -> bool:
        """Supprime une photo et son fichier"""
        photo = self.get(db=db, id=id)
        if photo:
            # Supprimer le fichier
            ImageHandler.delete_image(photo.filename)
            # Supprimer l'entrée en base
            db.delete(photo)
            db.commit()
            return True
        return False

# Créer une instance pour l'utiliser dans les routes
photo = CRUDPhoto(Photo) 