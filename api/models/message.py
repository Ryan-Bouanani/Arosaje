from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from utils.database import Base
import enum

class ConversationType(str, enum.Enum):
    PLANT_CARE = "plant_care"
    BOTANICAL_ADVICE = "botanical_advice"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(ConversationType))
    related_id = Column(Integer, nullable=True)  # ID de la garde ou du conseil associé
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    participants = relationship("ConversationParticipant", back_populates="conversation", cascade="all, delete-orphan")
    plant_care = relationship("PlantCare", back_populates="conversation", uselist=False)
    typing_users = relationship("UserTypingStatus", back_populates="conversation", cascade="all, delete-orphan")

class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_read_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User", back_populates="conversations")

    def to_dict(self):
        """Convertit l'objet en dictionnaire avec des types cohérents"""
        return {
            "id": int(self.id),
            "conversation_id": int(self.conversation_id),
            "user_id": int(self.user_id),
            "last_read_at": self.last_read_at.isoformat() if self.last_read_at else None
        }

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(2000), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    # Relations
    sender = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")

    def to_dict(self):
        """Convertit l'objet en dictionnaire avec des types cohérents"""
        return {
            "id": int(self.id),
            "content": str(self.content),
            "sender_id": int(self.sender_id) if self.sender_id else None,
            "conversation_id": int(self.conversation_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_read": bool(self.is_read)
        } 