from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from utils.database import Base


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Champs anglais standard
    name = Column(String, nullable=False)
    species = Column(String, nullable=True)
    description = Column(String, nullable=True)
    photo_base64 = Column(Text, nullable=True)  # Image complète encodée en Base64
    photo_thumbnail = Column(Text, nullable=True)  # Thumbnail 150x150 pour listes
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relations
    owner = relationship("User", back_populates="owned_plants")
    photos = relationship("Photo", back_populates="plant", cascade="all, delete-orphan")

    # Relations avec les gardes
    cares = relationship("PlantCare", back_populates="plant")
