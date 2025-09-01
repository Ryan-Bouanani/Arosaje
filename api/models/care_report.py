from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from utils.database import Base
import enum

class HealthLevel(str, enum.Enum):
    BAS = "Bas"
    MOYEN = "Moyen"
    BON = "Bon"

class CareReport(Base):
    __tablename__ = "care_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_care_id = Column(Integer, ForeignKey("plant_cares.id", ondelete="CASCADE"), nullable=False)
    caretaker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Informations de la séance
    session_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    photo_url = Column(String, nullable=True)
    
    # Évaluations de santé
    health_level = Column(Enum(HealthLevel), nullable=False)
    hydration_level = Column(Enum(HealthLevel), nullable=False)
    vitality_level = Column(Enum(HealthLevel), nullable=False)
    
    # Description détaillée
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    plant_care = relationship("PlantCare", back_populates="care_reports")
    caretaker = relationship("User", foreign_keys=[caretaker_id])
    botanist_advices = relationship("BotanistReportAdvice", back_populates="care_report")