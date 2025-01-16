from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from utils.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telephone = Column(String, nullable=True)
    password = Column(String, nullable=False)
    localisation = Column(String, nullable=True)

    # Relations
    owned_plants = relationship("Plant", back_populates="owner", cascade="all, delete-orphan")  # Propriétaire
    created_advices = relationship("Advice", back_populates="botanist")  # Botaniste

    # Relations avec les gardes
    plants_given_for_care = relationship("PlantCare", foreign_keys="PlantCare.owner_id", back_populates="owner")
    plants_taken_for_care = relationship("PlantCare", foreign_keys="PlantCare.caretaker_id", back_populates="caretaker")
