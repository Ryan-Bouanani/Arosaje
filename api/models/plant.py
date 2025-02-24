from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base

class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    espece = Column(String, nullable=True)
    description = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Propriétaire de la plante

    # Relations
    owner = relationship("User", back_populates="owned_plants")
    advices = relationship("Advice", back_populates="plant", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="plant", cascade="all, delete-orphan")

    # Relations avec les gardes
    cares = relationship("PlantCare", back_populates="plant")
