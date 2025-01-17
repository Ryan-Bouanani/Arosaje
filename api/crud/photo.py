from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from models.photo import Photo
from schemas.photo import PhotoCreate, PhotoResponse
from .base import CRUDBase
from utils.image_handler import ImageHandler
from fastapi import HTTPException
import json
from utils.redis_client import get_redis_client

class CRUDPhoto(CRUDBase[Photo, PhotoCreate, PhotoCreate]):
    def __init__(self, model: Photo):
        super().__init__(model)
        self.redis_client = get_redis_client()
        self.cache_ttl = 3600  # 1 heure

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
        """Supprime une photo, son fichier et invalide le cache"""
        photo = self.get(db=db, id=id)
        if photo:
            # Invalider le cache
            self.redis_client.delete(f"plant_photos:{photo.plant_id}")
            
            # Supprimer le fichier
            ImageHandler.delete_image(photo.filename)
            
            # Supprimer l'entrée en base
            db.delete(photo)
            db.commit()
            return True
        return False

    def get_plant_photos(self, db: Session, plant_id: int) -> Dict[str, List[PhotoResponse]]:
        # Vérifier le cache Redis
        cache_key = f"plant_photos:{plant_id}"
        cached_photos = self.redis_client.get(cache_key)
        
        if cached_photos:
            return {"photos": json.loads(cached_photos)}
            
        # Si pas en cache, récupérer depuis la base de données
        photos = db.query(Photo).filter(Photo.plant_id == plant_id).all()
        
        # Convertir en PhotoResponse avec sérialisation JSON automatique
        photos_data = [
            PhotoResponse(
                id=photo.id,
                filename=photo.filename,
                url=photo.url,
                plant_id=photo.plant_id,
                description=photo.description,
                type=photo.type,
                created_at=photo.created_at
            ).model_dump(mode='json')
            for photo in photos
        ]
        
        # Mettre en cache
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(photos_data)  # Plus besoin de l'encodeur personnalisé
        )
        
        return {"photos": photos_data}

    def create_photo(self, db: Session, photo: PhotoCreate) -> Photo:
        db_photo = Photo(**photo.model_dump())
        db.add(db_photo)
        db.commit()
        db.refresh(db_photo)
        
        # Invalider le cache des photos de la plante
        self.redis_client.delete(f"plant_photos:{photo.plant_id}")
        
        return db_photo

    def delete_photo(self, db: Session, photo_id: int) -> bool:
        photo = db.query(Photo).filter(Photo.id == photo_id).first()
        if not photo:
            raise HTTPException(status_code=404, detail="Photo non trouvée")
            
        # Invalider le cache avant la suppression
        self.redis_client.delete(f"plant_photos:{photo.plant_id}")
        
        db.delete(photo)
        db.commit()
        return True

# Créer une instance pour l'utiliser dans les routes
photo = CRUDPhoto(Photo) 