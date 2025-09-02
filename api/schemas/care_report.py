from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from models.care_report import HealthLevel


class CareReportBase(BaseModel):
    plant_care_id: int
    health_level: HealthLevel
    hydration_level: HealthLevel
    vitality_level: HealthLevel
    description: Optional[str] = None


class CareReportCreate(CareReportBase):
    pass


class CareReportInDB(CareReportBase):
    id: int
    caretaker_id: int
    session_date: datetime
    photo_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Schémas pour les objets liés
class UserSimple(BaseModel):
    id: int
    prenom: str
    nom: Optional[str] = None

    model_config = {"from_attributes": True}


class PlantSimple(BaseModel):
    id: int
    nom: str
    espece: Optional[str] = None

    model_config = {"from_attributes": True}


class PlantCareSimple(BaseModel):
    id: int
    plant: Optional[PlantSimple] = None

    model_config = {"from_attributes": True}


# Schéma pour les avis de botaniste
class BotanistAdviceSimple(BaseModel):
    id: int
    advice_text: str
    created_at: datetime
    botanist: Optional[UserSimple] = None

    model_config = {"from_attributes": True}


class CareReport(CareReportInDB):
    botanist_advices: Optional[List[BotanistAdviceSimple]] = []


class CareReportWithDetails(CareReport):
    caretaker: Optional[UserSimple] = None
    plant_care: Optional[PlantCareSimple] = None
    botanist_advices: Optional[List[BotanistAdviceSimple]] = []
