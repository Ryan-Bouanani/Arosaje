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

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ConversationType), nullable=False)
    related_id = Column(Integer, nullable=True)  # ID de la garde ou de la demande de conseil
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    participants = relationship("ConversationParticipant", back_populates="conversation", cascade="all, delete-orphan")
    plant_care = relationship("PlantCare", back_populates="conversation", uselist=False)

class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_read_at = Column(DateTime, nullable=True)

    # Relations
    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User", back_populates="conversations")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(2000), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    # Relations
    sender = relationship("User", back_populates="sent_messages")
    conversation = relationship("Conversation", back_populates="messages") 