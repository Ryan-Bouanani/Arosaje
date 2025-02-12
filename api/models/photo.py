from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from utils.database import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)  # 'plant', 'garde_start', 'garde_end'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    plant_id = Column(Integer, ForeignKey("plants.id"))
    plant = relationship("Plant", back_populates="photos") 