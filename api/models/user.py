from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from utils.database import Base

class UserRole(str, enum.Enum):
    USER = "user"
    BOTANIST = "botanist"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    nom = Column(String)
    prenom = Column(String)
    telephone = Column(String)
    localisation = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_verified = Column(Boolean, default=False)  # Par défaut, les comptes ne sont pas vérifiés

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

    def get_full_name(self) -> str:
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.prenom} {self.nom}"
