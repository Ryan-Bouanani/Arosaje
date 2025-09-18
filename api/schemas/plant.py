from typing import Optional
from .base import BaseSchema, IDSchema


class PlantBase(BaseSchema):
    # Nouveaux champs anglais (standard technique)
    name: str
    species: Optional[str] = None
    description: Optional[str] = None
    photo_base64: Optional[str] = None  # Image encodée en Base64
    owner_id: int
    # Anciens champs français (compatibilité temporaire)
    nom: Optional[str] = None
    espece: Optional[str] = None


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseSchema):
    # Nouveaux champs anglais
    name: Optional[str] = None
    species: Optional[str] = None
    description: Optional[str] = None
    photo_base64: Optional[str] = None
    owner_id: Optional[int] = None
    # Anciens champs français (compatibilité temporaire)
    nom: Optional[str] = None
    espece: Optional[str] = None


class Plant(PlantBase, IDSchema):
    pass
