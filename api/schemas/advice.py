from pydantic import BaseModel

class AdviceBase(BaseModel):
    texte: str
    date: str
    plant_id: int

class AdviceCreate(AdviceBase):
    botanist_id: int

class AdviceResponse(AdviceBase):
    id: int

    class Config:
        from_attributes = True
