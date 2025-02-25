from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, File, UploadFile, Form
from sqlalchemy.orm import Session
from crud.plant import plant
from schemas.plant import Plant, PlantCreate, PlantUpdate
from utils.database import get_db
from utils.security import get_current_user
from utils.image_handler import ImageHandler

router = APIRouter(
    prefix="/plants",
    tags=["plants"]
)

@router.get("/", response_model=List[Plant])
def read_plants(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    owner_id: Optional[int] = Query(None)
):
    """Liste toutes les plantes avec pagination optionnelle"""
    if owner_id:
        plants = plant.get_by_owner(db, owner_id=owner_id, skip=skip, limit=limit)
    else:
        plants = plant.get_multi(db, skip=skip, limit=limit)
    return plants

@router.post("/", response_model=Plant)
async def create_plant(
    nom: str = Form(...),
    espece: str = Form(None),
    description: str = Form(None),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crée une nouvelle plante"""
    try:
        # Créer l'objet PlantCreate avec les données du formulaire
        plant_data = {
            "nom": nom,
            "espece": espece,
            "description": description,
            "owner_id": current_user.id
        }

        # Si une photo est fournie, la sauvegarder
        if photo:
            filename, photo_url = await ImageHandler.save_image(photo, "persisted")
            plant_data["photo"] = photo_url

        # Créer la plante
        plant_in = PlantCreate(**plant_data)
        result = plant.create(db=db, obj_in=plant_in)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la création de la plante: {str(e)}"
        )

@router.get("/{plant_id}", response_model=Plant)
def read_plant(
    plant_id: int,
    db: Session = Depends(get_db)
):
    """Récupère une plante spécifique"""
    db_plant = plant.get(db=db, id=plant_id)
    if db_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return db_plant

@router.put("/{plant_id}", response_model=Plant)
def update_plant(
    *,
    db: Session = Depends(get_db),
    plant_id: int,
    plant_in: PlantUpdate
):
    """Met à jour une plante"""
    db_plant = plant.get(db=db, id=plant_id)
    if db_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant.update(db=db, db_obj=db_plant, obj_in=plant_in)

@router.delete("/{plant_id}", response_model=Plant)
def delete_plant(
    *,
    db: Session = Depends(get_db),
    plant_id: int
):
    """Supprime une plante"""
    db_plant = plant.get(db=db, id=plant_id)
    if db_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant.delete(db=db, id=plant_id) 