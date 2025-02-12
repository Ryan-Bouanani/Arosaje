from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime
import enum

class AdviceStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"

class Advice(Base):
    __tablename__ = "advices"
    id = Column(Integer, primary_key=True, index=True)
    texte = Column(String, nullable=False)
    status = Column(Enum(AdviceStatus), default=AdviceStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    botanist_id = Column(Integer, ForeignKey("users.id"))  # Botaniste ayant créé le conseil
    plant_id = Column(Integer, ForeignKey("plants.id"))  # Plante liée au conseil

    # Relations
    botanist = relationship("User", back_populates="created_advices")
    plant = relationship("Plant", back_populates="advices")
