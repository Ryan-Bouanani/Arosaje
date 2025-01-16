from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.advice import AdviceStatus

class AdviceBase(BaseModel):
    texte: str
    plant_id: int

class AdviceCreate(AdviceBase):
    pass

class AdviceUpdate(BaseModel):
    texte: Optional[str] = None
    status: Optional[AdviceStatus] = None

class AdviceInDB(AdviceBase):
    id: int
    status: AdviceStatus
    created_at: datetime
    updated_at: datetime
    botanist_id: int

    class Config:
        from_attributes = True

class Advice(AdviceInDB):
    pass
