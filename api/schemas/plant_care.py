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

    @property
    def username(self) -> str:
        """Retourne le nom complet comme username"""
        return f"{self.first_name} {self.last_name}"

    model_config = {"from_attributes": True}


class PlantBase(BaseModel):
    id: int
    name: Optional[str] = None
    species: Optional[str] = None
    photo: Optional[str] = None
    # Images: full et thumbnail pour optimisation
    photo_base64: Optional[str] = None
    photo_thumbnail: Optional[str] = None

    model_config = {"from_attributes": True}


class PlantOptimized(BaseModel):
    """Version optimisée pour les listes - avec thumbnails OU full images selon flag"""
    id: int
    name: Optional[str] = None
    species: Optional[str] = None
    # Image optimisée: thumbnail si disponible, sinon photo_base64 en fallback
    photo_thumbnail: Optional[str] = None
    photo_base64: Optional[str] = None  # Fallback si pas de thumbnail

    model_config = {"from_attributes": True}


class PlantCareBase(BaseModel):
    plant_id: int
    start_date: datetime
    end_date: datetime
    care_instructions: Optional[str] = None
    location: Optional[str] = None
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
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None

    @field_validator("end_date")
    def end_date_must_be_after_start_date(cls, v, info):
        if v and "start_date" in info.data and info.data["start_date"] and v <= info.data["start_date"]:
            raise ValueError("La date de fin doit être postérieure à la date de début")
        return v


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


# FEATURE FLAG: Choisir la version à utiliser facilement
USE_THUMBNAILS = False  # True = PlantOptimized, False = PlantBase (rollback)

class PlantCareList(PlantCareBase):
    """Version pour les listes avec feature flag pour rollback facile"""
    id: int
    owner_id: int
    caretaker_id: Optional[int] = None
    status: CareStatus = CareStatus.PENDING
    conversation_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # FEATURE FLAG: PlantOptimized (thumbnails) OU PlantBase (full images)
    plant: PlantBase  # Utiliser PlantBase pour l'instant (rollback)
    owner: Optional[UserBase] = None
    caretaker: Optional[UserBase] = None

    model_config = {"from_attributes": True}


class PlantCareListOptimized(PlantCareBase):
    """Version optimisée pour les listes - avec thumbnails"""
    id: int
    owner_id: int
    caretaker_id: Optional[int] = None
    status: CareStatus = CareStatus.PENDING
    conversation_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    plant: PlantOptimized  # Utilise PlantOptimized avec thumbnails
    owner: Optional[UserBase] = None
    caretaker: Optional[UserBase] = None

    model_config = {"from_attributes": True}


class PlantCare(PlantCareInDB):
    pass
