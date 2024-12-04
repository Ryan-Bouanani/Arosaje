from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telephone = Column(String, nullable=True)
    role = Column(String, nullable=False)  # Propriétaire, Gardien, Botaniste
    mot_de_passe = Column(String, nullable=False)
    localisation = Column(String, nullable=True)

    plants = relationship("Plant", back_populates="owner")
    advices = relationship("Advice", back_populates="botanist")
    gardes = relationship("Garde", back_populates="gardien")
