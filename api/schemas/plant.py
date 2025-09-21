from typing import Optional
from .base import BaseSchema, IDSchema


class PlantBase(BaseSchema):
    # Champs anglais standard
    name: Optional[str] = None
    species: Optional[str] = None
    description: Optional[str] = None
    photo_base64: Optional[str] = None  # Image encodée en Base64
    owner_id: int

    class Config:
        from_attributes = True


class PlantCreate(PlantBase):
    # Pour la création, name est requis
    name: str  # Requis pour la création


class PlantUpdate(BaseSchema):
    # Champs anglais standard
    name: Optional[str] = None
    species: Optional[str] = None
    description: Optional[str] = None
    photo_base64: Optional[str] = None
    owner_id: Optional[int] = None


class Plant(PlantBase, IDSchema):
    pass
