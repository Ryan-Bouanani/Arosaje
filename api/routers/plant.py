from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
import base64
from crud.plant import plant
from schemas.plant import Plant, PlantCreate, PlantUpdate
from utils.database import get_db
from utils.security import get_current_user

router = APIRouter(prefix="/plants", tags=["plants"])


@router.get("/", response_model=List[Plant])
def read_plants(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    owner_id: Optional[int] = Query(None),
):
    """Lister toutes les plantes avec pagination optionnelle"""
    if owner_id:
        plants = plant.get_by_owner(db, owner_id=owner_id, skip=skip, limit=limit)
    else:
        plants = plant.get_multi(db, skip=skip, limit=limit)
    return plants


@router.post("/", response_model=Plant)
async def create_plant(
    name: str = Form(...),
    species: str = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Créer une nouvelle plante"""
    try:
        # Créer l'objet PlantCreate avec les données du formulaire
        plant_data = {
            "name": name,
            "species": species,
            "owner_id": current_user.id,
            "photo_base64": None  # Initialiser à None par défaut
        }

        # Si une photo est fournie, l'encoder en Base64
        if photo and photo.filename:  # Vérifier aussi que le fichier a un nom
            # Validation basée sur l'extension du fichier (Flutter envoie souvent application/octet-stream)
            filename_lower = photo.filename.lower()
            if not filename_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                raise HTTPException(status_code=400, detail="Le fichier doit être une image (jpg, jpeg, png, gif, webp)")
            
            # Déterminer le type MIME basé sur l'extension
            if filename_lower.endswith(('.jpg', '.jpeg')):
                mime_type = "image/jpeg"
            elif filename_lower.endswith('.png'):
                mime_type = "image/png"
            elif filename_lower.endswith('.gif'):
                mime_type = "image/gif"
            elif filename_lower.endswith('.webp'):
                mime_type = "image/webp"
            else:
                mime_type = "image/jpeg"  # Fallback
            
            # Lire le contenu de l'image
            await photo.seek(0)
            image_data = await photo.read()
            
            # Vérifier la taille (max 5MB pour éviter des problèmes de DB)
            if len(image_data) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="L'image ne peut pas dépasser 5MB")
            
            # Encoder en Base64
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Créer le data URL avec le type MIME correct
            data_url = f"data:{mime_type};base64,{base64_image}"
            plant_data["photo_base64"] = data_url

        # Créer la plante
        plant_in = PlantCreate(**plant_data)
        result = plant.create(db=db, obj_in=plant_in, owner_id=current_user.id)
        return result
    except Exception as e:
        import traceback
        print(f"ERROR in create_plant: {str(e)}")
        print(f"TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la création de la plante: {str(e)}"
        )


@router.get("/{plant_id}", response_model=Plant)
def read_plant(plant_id: int, db: Session = Depends(get_db)):
    """Récupérer une plante spécifique par son ID"""
    db_plant = plant.get(db=db, id=plant_id)
    if db_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return db_plant


@router.put("/{plant_id}", response_model=Plant)
def update_plant(
    *, db: Session = Depends(get_db), plant_id: int, plant_in: PlantUpdate
):
    """Mettre à jour les informations d'une plante"""
    db_plant = plant.get(db=db, id=plant_id)
    if db_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant.update(db=db, db_obj=db_plant, obj_in=plant_in)


@router.delete("/{plant_id}", response_model=Plant)
def delete_plant(*, db: Session = Depends(get_db), plant_id: int):
    """Supprimer définitivement une plante"""
    db_plant = plant.get(db=db, id=plant_id)
    if db_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant.delete(db=db, id=plant_id)


