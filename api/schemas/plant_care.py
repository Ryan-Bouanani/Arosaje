from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from models.plant_care import CareStatus

class PlantBase(BaseModel):
    id: int
    nom: str
    espece: Optional[str] = None
    photo: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class PlantCareBase(BaseModel):
    plant_id: int
    start_date: datetime
    end_date: datetime
    care_instructions: Optional[str] = None
    localisation: Optional[str] = None

    @field_validator('end_date')
    def end_date_must_be_after_start_date(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('La date de fin doit être postérieure à la date de début')
        return v

class PlantCareCreate(PlantCareBase):
    caretaker_id: Optional[int] = None

class PlantCareUpdate(BaseModel):
    status: Optional[CareStatus] = None
    care_instructions: Optional[str] = None
    start_photo_url: Optional[str] = None
    end_photo_url: Optional[str] = None
    conversation_id: Optional[int] = None

class PlantCareInDB(PlantCareBase):
    id: int
    owner_id: int
    caretaker_id: Optional[int] = None
    status: CareStatus = CareStatus.PENDING
    start_photo_url: Optional[str] = None
    end_photo_url: Optional[str] = None
    conversation_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    plant: PlantBase

    model_config = {
        "from_attributes": True
    }

class PlantCare(PlantCareInDB):
    pass