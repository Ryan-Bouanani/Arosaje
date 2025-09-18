from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from utils.database import Base


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Anciens champs français (compatibilité temporaire)
    nom = Column(String, nullable=False)
    espece = Column(String, nullable=True)
    # Nouveaux champs anglais
    name = Column(String, nullable=True)
    species = Column(String, nullable=True)
    description = Column(String, nullable=True)
    photo_base64 = Column(Text, nullable=True)  # Image encodée en Base64
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relations
    owner = relationship("User", back_populates="owned_plants")
    photos = relationship("Photo", back_populates="plant", cascade="all, delete-orphan")

    # Relations avec les gardes
    cares = relationship("PlantCare", back_populates="plant")
