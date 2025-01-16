from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.advice import AdviceStatus
from models.user import UserRole
from schemas.advice import Advice, AdviceCreate, AdviceUpdate
from crud import advice as crud_advice
from utils.database import get_db
from utils.security import get_current_user

router = APIRouter(
    prefix="/advices",
    tags=["advices"]
)

@router.post("/", response_model=Advice)
def create_advice(
    advice: AdviceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Créer un nouveau conseil (réservé aux botanistes)"""
    return crud_advice.create_advice(db=db, advice=advice, botanist_id=current_user.id)

@router.get("/plant/{plant_id}", response_model=List[Advice])
def get_plant_advices(
    plant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtenir tous les conseils pour une plante donnée"""
    return crud_advice.get_advices_by_plant(db, plant_id=plant_id, skip=skip, limit=limit)

@router.get("/botanist/{botanist_id}", response_model=List[Advice])
def get_botanist_advices(
    botanist_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtenir tous les conseils donnés par un botaniste"""
    return crud_advice.get_advices_by_botanist(db, botanist_id=botanist_id, skip=skip, limit=limit)

@router.get("/{advice_id}", response_model=Advice)
def get_advice(
    advice_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtenir un conseil spécifique"""
    db_advice = crud_advice.get_advice(db, advice_id=advice_id)
    if db_advice is None:
        raise HTTPException(status_code=404, detail="Conseil non trouvé")
    return db_advice

@router.put("/{advice_id}", response_model=Advice)
def update_advice(
    advice_id: int,
    advice_update: AdviceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mettre à jour un conseil (réservé au botaniste qui l'a créé)"""
    db_advice = crud_advice.get_advice(db, advice_id=advice_id)
    if db_advice is None:
        raise HTTPException(status_code=404, detail="Conseil non trouvé")
    if db_advice.botanist_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas modifier ce conseil")
    return crud_advice.update_advice(db=db, advice_id=advice_id, advice_update=advice_update)

@router.put("/{advice_id}/validate", response_model=Advice)
def validate_advice(
    advice_id: int,
    status: AdviceStatus,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Valider ou rejeter un conseil (réservé aux botanistes)"""
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(status_code=403, detail="Seuls les botanistes peuvent valider les conseils")
    return crud_advice.validate_advice(db=db, advice_id=advice_id, status=status)

@router.delete("/{advice_id}", response_model=Advice)
def delete_advice(
    advice_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Supprimer un conseil (réservé au botaniste qui l'a créé)"""
    db_advice = crud_advice.get_advice(db, advice_id=advice_id)
    if db_advice is None:
        raise HTTPException(status_code=404, detail="Conseil non trouvé")
    if db_advice.botanist_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas supprimer ce conseil")
    return crud_advice.delete_advice(db=db, advice_id=advice_id) 