from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.security import get_current_user
from utils.image_handler import ImageHandler
from crud.photo import photo as photo_crud
from schemas.photo import PhotoResponse, PhotoCreate
from models.photo import Photo
from datetime import datetime

router = APIRouter(
    prefix="/photos",
    tags=["photos"]
)

@router.post("/upload/{plant_id}", response_model=PhotoResponse)
async def upload_photo(
    plant_id: int,
    type: str,
    description: str | None = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload une nouvelle photo pour une plante"""
    try:
        # Vérifier le type de fichier
        if not ImageHandler.is_valid_image(file):
            raise HTTPException(
                status_code=400,
                detail="Format de fichier non supporté. Utilisez JPG, JPEG, PNG ou GIF"
            )
            
        filename, url = await ImageHandler.save_image(file, type)

        # Créer l'entrée en base
        photo_data = {
            "filename": filename,
            "url": url,
            "plant_id": plant_id,
            "description": description,
            "type": type,
            "created_at": datetime.utcnow()
        }
        
        photo_in = PhotoCreate(**photo_data)
        photo = photo_crud.create_photo(db=db, photo=photo_in)

        # Convertir en réponse
        return PhotoResponse(
            id=photo.id,
            filename=photo.filename,
            url=photo.url,
            plant_id=photo.plant_id,
            description=photo.description,
            type=photo.type,
            created_at=photo.created_at
        )

    except Exception as e:
        # En cas d'erreur, supprimer le fichier si créé
        if 'filename' in locals():
            ImageHandler.delete_image(filename)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/plant/{plant_id}", response_model=Dict[str, List[PhotoResponse]])
def get_plant_photos(
    plant_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, List[PhotoResponse]]:
    """Récupère toutes les photos d'une plante"""
    return photo_crud.get_plant_photos(db=db, plant_id=plant_id)

@router.delete("/{photo_id}")
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Supprime une photo"""
    if photo_crud.delete_with_file(db=db, id=photo_id):
        return {"message": "Photo supprimée avec succès"}
    raise HTTPException(status_code=404, detail="Photo non trouvée") 