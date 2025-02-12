from typing import Optional
from pydantic import BaseModel
from .base import BaseSchema, IDSchema

class PlantBase(BaseSchema):
    nom: str
    espece: Optional[str] = None
    description: Optional[str] = None
    photo: Optional[str] = None
    owner_id: int

class PlantCreate(PlantBase):
    pass

class PlantUpdate(PlantBase):
    nom: Optional[str] = None
    owner_id: Optional[int] = None

class Plant(PlantBase, IDSchema):
    pass 