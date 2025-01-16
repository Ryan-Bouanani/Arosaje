from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from utils.database import Base
import enum

class CareStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFUSED = "refused"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PlantCare(Base):
    __tablename__ = "plant_cares"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    caretaker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(Enum(CareStatus), default=CareStatus.PENDING)
    
    care_instructions = Column(String, nullable=True)
    start_photo_url = Column(String, nullable=True)
    end_photo_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    plant = relationship("Plant", back_populates="cares")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="plants_given_for_care")
    caretaker = relationship("User", foreign_keys=[caretaker_id], back_populates="plants_taken_for_care")