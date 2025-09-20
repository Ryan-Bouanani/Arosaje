from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from models.plant_care import CareStatus


class UserBase(BaseModel):
    id: int
    # Nouveaux champs anglais
    first_name: str
    last_name: str
    email: str
    location: Optional[str] = None
    # Anciens champs français (compatibilité temporaire)
    nom: Optional[str] = None
    prenom: Optional[str] = None
    localisation: Optional[str] = None

    @property
    def username(self) -> str:
        """Retourne le nom complet comme username"""
        # Utiliser les nouveaux champs anglais en priorité
        if hasattr(self, 'first_name') and hasattr(self, 'last_name'):
            return f"{self.first_name} {self.last_name}"
        # Fallback vers les anciens champs français
        return f"{self.first_name or self.prenom or ''} {self.last_name or self.nom or ''}"

    model_config = {"from_attributes": True}


class PlantBase(BaseModel):
    id: int
    # Nouveaux champs anglais - compatibilité avec données existantes
    name: Optional[str] = None
    species: Optional[str] = None
    photo: Optional[str] = None
    photo_base64: Optional[str] = None
    # Anciens champs français (compatibilité temporaire)
    nom: Optional[str] = None
    espece: Optional[str] = None

    model_config = {"from_attributes": True}


class PlantCareBase(BaseModel):
    plant_id: int
    start_date: datetime
    end_date: datetime
    care_instructions: Optional[str] = None
    location: Optional[str] = None
    # Ancien champ français (compatibilité temporaire)
    localisation: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("end_date")
    def end_date_must_be_after_start_date(cls, v, info):
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("La date de fin doit être postérieure à la date de début")
        return v


class PlantCareCreate(PlantCareBase):
    caretaker_id: Optional[int] = None


class PlantCareUpdate(BaseModel):
    status: Optional[CareStatus] = None
    care_instructions: Optional[str] = None
    conversation_id: Optional[int] = None


class PlantCareInDB(PlantCareBase):
    id: int
    owner_id: int
    caretaker_id: Optional[int] = None
    status: CareStatus = CareStatus.PENDING
    conversation_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    plant: PlantBase
    owner: Optional[UserBase] = None
    caretaker: Optional[UserBase] = None

    model_config = {"from_attributes": True}


class PlantCare(PlantCareInDB):
    pass
