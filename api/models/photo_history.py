from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class PhotoHistory(Base):
    __tablename__ = "photo_histories"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    photo = Column(String, nullable=False)
    description = Column(String, nullable=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))

    plant = relationship("Plant", back_populates="photo_histories")
