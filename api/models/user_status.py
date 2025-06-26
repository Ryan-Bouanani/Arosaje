from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from utils.database import Base

class UserStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"

class UserTypingStatus(Base):
    __tablename__ = "user_typing_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    is_typing = Column(Boolean, default=False)
    last_typed_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="typing_status")
    conversation = relationship("Conversation", back_populates="typing_users")

class UserPresence(Base):
    __tablename__ = "user_presence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    status = Column(Enum(UserStatus), default=UserStatus.OFFLINE)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    socket_id = Column(String, nullable=True)  # Pour gérer les connexions multiples

    # Relations
    user = relationship("User", back_populates="presence") 