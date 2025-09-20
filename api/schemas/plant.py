from typing import Optional
from .base import BaseSchema, IDSchema


class PlantBase(BaseSchema):
    # Champs principaux - accepte les deux formats nom/name et espece/species
    name: Optional[str] = None
    species: Optional[str] = None
    description: Optional[str] = None
    photo_base64: Optional[str] = None  # Image encodée en Base64
    owner_id: int
    # Champs français pour compatibilité
    nom: Optional[str] = None
    espece: Optional[str] = None

    def model_post_init(self, __context) -> None:
        """Map les champs français vers anglais pour compatibilité frontend"""
        if self.name is None and self.nom:
            self.name = self.nom
        if self.species is None and self.espece:
            self.species = self.espece

    class Config:
        from_attributes = True


class PlantCreate(PlantBase):
    # Pour la création, au moins nom doit être fourni
    nom: str  # Requis pour la création


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
