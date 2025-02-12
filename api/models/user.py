from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum
from utils.database import Base

class UserRole(str, enum.Enum):
    USER = "user"
    BOTANIST = "botanist"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    nom = Column(String)
    prenom = Column(String)
    telephone = Column(String)
    localisation = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)

    # Relations
    owned_plants = relationship("Plant", back_populates="owner")
    plants_given_for_care = relationship("PlantCare", foreign_keys="[PlantCare.owner_id]", back_populates="owner")
    plants_taken_for_care = relationship("PlantCare", foreign_keys="[PlantCare.caretaker_id]", back_populates="caretaker")
    created_advices = relationship("Advice", back_populates="botanist")
    messages = relationship("Message", back_populates="sender")
    conversations = relationship("ConversationParticipant", back_populates="user")

    # Relations pour le statut
    typing_status = relationship("UserTypingStatus", back_populates="user", uselist=True)
    presence = relationship("UserPresence", back_populates="user", uselist=False)
