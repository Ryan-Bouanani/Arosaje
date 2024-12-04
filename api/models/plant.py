from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    espece = Column(String, nullable=True)
    description = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))  # Propriétaire de la plante

    # Relations
    owner = relationship("User", back_populates="owned_plants")
    gardes = relationship("Garde", back_populates="plant", cascade="all, delete-orphan")
    advices = relationship("Advice", back_populates="plant", cascade="all, delete-orphan")
