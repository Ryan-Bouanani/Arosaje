from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from models.advice import AdviceStatus

class AdviceBase(BaseModel):
    id: Optional[int] = None
    texte: str
    plant_id: int
    status: Optional[AdviceStatus] = AdviceStatus.PENDING
    botanist_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Pour la création d'un conseil
class AdviceCreate(BaseModel):
    texte: str
    plant_id: int

# Pour la mise à jour d'un conseil
class AdviceUpdate(BaseModel):
    texte: Optional[str] = None
    status: Optional[AdviceStatus] = None

# Pour les réponses individuelles
class Advice(AdviceBase):
    pass

# Pour les réponses contenant une liste
class AdviceResponse(BaseModel):
    advices: List[Advice] = []
