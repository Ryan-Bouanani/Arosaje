from pydantic import BaseModel

class PlantBase(BaseModel):
    nom: str
    espece: str | None = None
    description: str | None = None
    photo: str | None = None

class PlantCreate(PlantBase):
    owner_id: int

class PlantResponse(PlantBase):
    id: int

    class Config:
        orm_mode = True
