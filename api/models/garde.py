from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Garde(Base):
    __tablename__ = "gardes"
    id = Column(Integer, primary_key=True, index=True)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)
    photo = Column(String, nullable=True)
    statut = Column(String, nullable=False)  # En cours/Terminée
    gardien_id = Column(Integer, ForeignKey("users.id"))
    plant_id = Column(Integer, ForeignKey("plants.id"))

    gardien = relationship("User", back_populates="gardes")
    plant = relationship("Plant", back_populates="gardes")
