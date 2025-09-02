from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BotanistReportAdviceBase(BaseModel):
    care_report_id: int
    advice_text: str


class BotanistReportAdviceCreate(BotanistReportAdviceBase):
    pass


class BotanistReportAdviceUpdate(BaseModel):
    advice_text: str


class BotanistReportAdvice(BotanistReportAdviceBase):
    id: int
    botanist_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Schéma pour le botaniste
class BotanistSimple(BaseModel):
    id: int
    prenom: str
    nom: Optional[str] = None

    model_config = {"from_attributes": True}


# Schéma complet avec relations
class BotanistReportAdviceWithDetails(BotanistReportAdvice):
    botanist: Optional[BotanistSimple] = None
