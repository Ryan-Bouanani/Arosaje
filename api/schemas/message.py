from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ConversationType(str, Enum):
    PLANT_CARE = "plant_care"  # Conversation propriétaire ↔ gardien
    BOTANICAL_ADVICE = "botanical_advice"  # Conversation avec un botaniste

class MessageBase(BaseModel):
    content: str = Field(..., max_length=2000)

class MessageCreate(MessageBase):
    conversation_id: int

class Message(MessageBase):
    id: int
    sender_id: int
    conversation_id: int
    created_at: datetime
    updated_at: datetime
    is_read: bool

    class Config:
        from_attributes = True

class ConversationParticipant(BaseModel):
    user_id: int
    last_read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    type: ConversationType
    related_id: Optional[int] = None  # ID de la garde ou de la demande de conseil

class ConversationCreate(ConversationBase):
    participant_ids: List[int]

class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    participants: List[ConversationParticipant] = []

    class Config:
        from_attributes = True

class ConversationWithLastMessage(BaseModel):
    id: int
    type: ConversationType
    related_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    participants: List[ConversationParticipant]
    last_message: Optional[Message]
    unread_count: int

    class Config:
        from_attributes = True 