from sqlalchemy.orm import Session
from models.advice import Advice, AdviceStatus
from models.user import User, UserRole
from schemas.advice import AdviceCreate, AdviceUpdate
from fastapi import HTTPException

def get_advice(db: Session, advice_id: int):
    return db.query(Advice).filter(Advice.id == advice_id).first()

def get_advices_by_plant(db: Session, plant_id: int, skip: int = 0, limit: int = 100):
    return db.query(Advice).filter(Advice.plant_id == plant_id).offset(skip).limit(limit).all()

def get_advices_by_botanist(db: Session, botanist_id: int, skip: int = 0, limit: int = 100):
    return db.query(Advice).filter(Advice.botanist_id == botanist_id).offset(skip).limit(limit).all()

def create_advice(db: Session, advice: AdviceCreate, botanist_id: int):
    # Vérifier si l'utilisateur est un botaniste
    botanist = db.query(User).filter(User.id == botanist_id).first()
    if not botanist or botanist.role != UserRole.BOTANIST:
        raise HTTPException(status_code=403, detail="Seuls les botanistes peuvent créer des conseils")
    
    db_advice = Advice(**advice.model_dump(), botanist_id=botanist_id)
    db.add(db_advice)
    db.commit()
    db.refresh(db_advice)
    return db_advice

def update_advice(db: Session, advice_id: int, advice_update: AdviceUpdate):
    db_advice = get_advice(db, advice_id)
    if not db_advice:
        raise HTTPException(status_code=404, detail="Conseil non trouvé")
    
    update_data = advice_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_advice, field, value)
    
    db.commit()
    db.refresh(db_advice)
    return db_advice

def validate_advice(db: Session, advice_id: int, status: AdviceStatus):
    db_advice = get_advice(db, advice_id)
    if not db_advice:
        raise HTTPException(status_code=404, detail="Conseil non trouvé")
    
    db_advice.status = status
    db.commit()
    db.refresh(db_advice)
    return db_advice

def delete_advice(db: Session, advice_id: int):
    db_advice = get_advice(db, advice_id)
    if not db_advice:
        raise HTTPException(status_code=404, detail="Conseil non trouvé")
    
    db.delete(db_advice)
    db.commit()
    return db_advice 