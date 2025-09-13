from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.security import get_current_user
from utils.image_handler import ImageHandler
from crud.photo import photo as photo_crud
from schemas.photo import PhotoResponse, PhotoCreate
from datetime import datetime

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/upload/{plant_id}", response_model=PhotoResponse)
async def upload_photo(
    plant_id: int,
    type: str,
    description: str | None = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Uploader une photo pour une plante"""
    try:
        # Validation de base
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Le fichier doit être une image")
        
        # Lire le contenu de l'image
        await file.seek(0)
        image_data = await file.read()
        
        # Vérifier la taille (max 5MB pour éviter des problèmes de DB)
        if len(image_data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="L'image ne peut pas dépasser 5MB")
        
        # Encoder en Base64
        import base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Créer le data URL avec le type MIME
        data_url = f"data:{file.content_type};base64,{base64_image}"

        # Créer l'entrée en base
        photo_data = {
            "filename": file.filename or f"photo_{plant_id}_{type}.jpg",
            "url": "",  # Plus utilisé, on garde pour compatibilité
            "photo_base64": data_url,
            "plant_id": plant_id,
            "description": description,
            "type": type,
            "created_at": datetime.utcnow(),
        }

        photo_in = PhotoCreate(**photo_data)
        photo = photo_crud.create_photo(db=db, photo=photo_in)

        # Convertir en réponse
        return PhotoResponse(
            id=photo.id,
            filename=photo.filename,
            url=photo.url,
            photo_base64=photo.photo_base64,
            plant_id=photo.plant_id,
            description=photo.description,
            type=photo.type,
            created_at=photo.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'upload: {str(e)}")


@router.get("/plant/{plant_id}", response_model=Dict[str, List[PhotoResponse]])
def get_plant_photos(
    plant_id: int, db: Session = Depends(get_db)
) -> Dict[str, List[PhotoResponse]]:
    """Galerie de photos d'une plante"""
    return photo_crud.get_plant_photos(db=db, plant_id=plant_id)


@router.delete("/{photo_id}")
def delete_photo(
    photo_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Supprimer définitivement une photo"""
    if photo_crud.delete_with_file(db=db, id=photo_id):
        return {"message": "Photo supprimée avec succès"}
    raise HTTPException(status_code=404, detail="Photo non trouvée")
