from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base

class Advice(Base):
    __tablename__ = "advices"
    id = Column(Integer, primary_key=True, index=True)
    texte = Column(String, nullable=False)
    date = Column(String, nullable=False)
    botanist_id = Column(Integer, ForeignKey("users.id"))  # Botaniste ayant créé le conseil
    plant_id = Column(Integer, ForeignKey("plants.id"))  # Plante liée au conseil

    # Relations
    botanist = relationship("User", back_populates="created_advices")
    plant = relationship("Plant", back_populates="advices")
