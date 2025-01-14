from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from crud.plant import plant
from schemas.plant import Plant, PlantCreate, PlantUpdate
from utils.database import get_db
from utils.security import get_current_user

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
def create_plant(
    *,
    db: Session = Depends(get_db),
    plant_in: PlantCreate,
    current_user = Depends(get_current_user)
):
    """Crée une nouvelle plante"""
    plant_in.owner_id = current_user.id
    return plant.create(db=db, obj_in=plant_in)

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