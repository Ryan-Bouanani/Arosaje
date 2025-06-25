"""Modèles SQLAlchemy pour la nouvelle structure PostgreSQL."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "user"
    BOTANIST = "botanist"
    ADMIN = "admin"

class UserStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"

class AdviceStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"

class CareStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFUSED = "refused"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ConversationType(str, enum.Enum):
    PLANT_CARE = "plant_care"
    BOTANICAL_ADVICE = "botanical_advice"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    telephone = Column(String)
    localisation = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relations
    presence = relationship("UserPresence", back_populates="user", uselist=False)
    typing_status = relationship("UserTypingStatus", back_populates="user")
    owned_plants = relationship("Plant", back_populates="owner")
    created_advices = relationship("Advice", back_populates="botanist")
    sent_messages = relationship("Message", back_populates="sender")
    plant_cares_given = relationship("PlantCare", foreign_keys="[PlantCare.owner_id]", back_populates="owner")
    plant_cares_taken = relationship("PlantCare", foreign_keys="[PlantCare.caretaker_id]", back_populates="caretaker")
    conversation_participations = relationship("ConversationParticipant", back_populates="user")

class UserPresence(Base):
    __tablename__ = "user_presence"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    status = Column(Enum(UserStatus), default=UserStatus.OFFLINE)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    socket_id = Column(String)

    # Relations
    user = relationship("User", back_populates="presence")

class UserTypingStatus(Base):
    __tablename__ = "user_typing_status"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    is_typing = Column(Boolean, default=False)
    last_typed_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="typing_status")
    conversation = relationship("Conversation", back_populates="typing_users")

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    espece = Column(String)
    description = Column(String)
    photo = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relations
    owner = relationship("User", back_populates="owned_plants")
    photos = relationship("Photo", back_populates="plant")
    advices = relationship("Advice", back_populates="plant")
    care_sessions = relationship("PlantCare", back_populates="plant")

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)
    size_bytes = Column(Integer)
    photo_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))

    # Relations
    plant = relationship("Plant", back_populates="photos")

class Advice(Base):
    __tablename__ = "advices"

    id = Column(Integer, primary_key=True)
    texte = Column(String, nullable=False)
    status = Column(Enum(AdviceStatus), default=AdviceStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    botanist_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))

    # Relations
    botanist = relationship("User", back_populates="created_advices")
    plant = relationship("Plant", back_populates="advices")

class PlantCare(Base):
    __tablename__ = "plant_cares"

    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    caretaker_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="SET NULL"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(Enum(CareStatus), default=CareStatus.PENDING)
    care_instructions = Column(String)
    start_photo_url = Column(String)
    end_photo_url = Column(String)
    localisation = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    notes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relations
    plant = relationship("Plant", back_populates="care_sessions")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="plant_cares_given")
    caretaker = relationship("User", foreign_keys=[caretaker_id], back_populates="plant_cares_taken")
    conversation = relationship("Conversation", back_populates="plant_care")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    type = Column(Enum(ConversationType))
    related_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relations
    messages = relationship("Message", back_populates="conversation")
    participants = relationship("ConversationParticipant", back_populates="conversation")
    typing_users = relationship("UserTypingStatus", back_populates="conversation")
    plant_care = relationship("PlantCare", back_populates="conversation", uselist=False)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    attachments_count = Column(Integer, default=0)

    # Relations
    sender = relationship("User", back_populates="sent_messages")
    conversation = relationship("Conversation", back_populates="messages")

class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    last_read_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User", back_populates="conversation_participations") 