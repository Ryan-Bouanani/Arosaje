from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Garde(Base):
    __tablename__ = "gardes"
    id = Column(Integer, primary_key=True, index=True)
    date_debut = Column(String, nullable=False)
    date_fin = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    statut = Column(String, nullable=False)  # En cours/Terminée
    caretaker_id = Column(Integer, ForeignKey("users.id"))  # Gardien
    plant_id = Column(Integer, ForeignKey("plants.id"))  # Plante gardée

    # Relations
    caretaker = relationship("User", back_populates="caretaker_gardes")
    plant = relationship("Plant", back_populates="gardes")
