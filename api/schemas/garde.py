from pydantic import BaseModel

class GardeBase(BaseModel):
    date_debut: str
    date_fin: str | None = None
    photo: str | None = None
    statut: str
    plant_id: int

class GardeCreate(GardeBase):
    gardien_id: int

class GardeResponse(GardeBase):
    id: int

    class Config:
        orm_mode = True
