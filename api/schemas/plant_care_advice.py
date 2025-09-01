from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from models.plant_care_advice import AdvicePriority, ValidationStatus

class PlantCareAdviceBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str
    priority: AdvicePriority = AdvicePriority.NORMAL

class PlantCareAdviceCreate(PlantCareAdviceBase):
    plant_care_id: int

class PlantCareAdviceUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    priority: Optional[AdvicePriority] = None

class PlantCareAdviceValidation(BaseModel):
    validation_status: ValidationStatus
    validation_comment: Optional[str] = None

class BotanistInfo(BaseModel):
    id: int
    prenom: str
    nom: str
    email: str
    
    class Config:
        from_attributes = True

class PlantCareAdvice(PlantCareAdviceBase):
    id: int
    plant_care_id: int
    botanist_id: int
    validation_status: ValidationStatus
    validator_id: Optional[int] = None
    validation_comment: Optional[str] = None
    validated_at: Optional[datetime] = None
    version: int
    is_current_version: bool
    previous_version_id: Optional[int] = None
    owner_notified: bool
    botanist_notified: bool
    created_at: datetime
    updated_at: datetime
    
    # Relations
    botanist: Optional[BotanistInfo] = None
    validator: Optional[BotanistInfo] = None
    
    class Config:
        from_attributes = True

class PlantCareWithAdvice(BaseModel):
    id: int
    plant_id: int
    start_date: datetime
    end_date: datetime
    care_instructions: Optional[str] = None
    localisation: Optional[str] = None
    priority: AdvicePriority = AdvicePriority.NORMAL
    
    # Info de la plante
    plant_name: str
    plant_species: Optional[str] = None
    
    # Info propriétaire
    owner_name: str
    owner_email: str
    
    # Avis actuel (si existe)
    current_advice: Optional[PlantCareAdvice] = None
    
    # Historique des avis
    advice_history: List[PlantCareAdvice] = []
    
    # Statut de validation global
    needs_validation: bool = False
    validation_count: int = 0
    
    class Config:
        from_attributes = True

class AdviceStats(BaseModel):
    total_to_review: int
    total_reviewed: int
    urgent_count: int
    follow_up_count: int
    pending_validation: int
    my_advice_count: int
    my_validated_count: int = 0
    my_validations_done_count: int = 0