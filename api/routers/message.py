from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.security import get_current_user
from utils.rate_limiter import RateLimiter
from crud.message import message
from models.message import ConversationType
from schemas.message import (
    Message,
    MessageCreate,
    Conversation,
    ConversationCreate
)
from schemas.user import User
from services.email.email_service import EmailService

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

MESSAGE_RATE_LIMIT = 10  # messages par minute
TIME_WINDOW = 60  # secondes

email_service = EmailService()

@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle conversation"""
    return message.create_conversation(
        db=db,
        participant_ids=conversation.participant_ids,
        conversation_type=conversation.type,
        related_id=conversation.related_id
    )

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer une conversation par son ID"""
    conversation = message.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    return conversation

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les messages d'une conversation"""
    return message.get_conversation_messages(
        db,
        conversation_id=conversation_id,
        skip=skip,
        limit=limit
    )

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def create_message(
    conversation_id: int,
    message_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau message"""
    # Vérifier le rate limiting
    RateLimiter.check_rate_limit(
        user_id=current_user.id,
        action="send_message",
        max_requests=MESSAGE_RATE_LIMIT,
        time_window=TIME_WINDOW
    )

    if message_in.conversation_id != conversation_id:
        raise HTTPException(
            status_code=400,
            detail="L'ID de conversation dans l'URL ne correspond pas à celui du message"
        )
    new_message = message.create_message(
        db=db,
        message=message_in,
        sender_id=current_user.id
    )
    
    # Récupérer les autres participants de la conversation
    participants = await get_conversation_participants(conversation_id)
    
    # Envoyer une notification par email à chaque participant (sauf l'expéditeur)
    for participant in participants:
        if participant.id != current_user.id:
            await email_service.send_new_message_notification(
                recipient_email=participant.email,
                sender_name=current_user.username,
                conversation_id=conversation_id
            )
    
    return new_message

@router.post("/conversations/{conversation_id}/read", response_model=dict)
async def mark_conversation_as_read(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marquer tous les messages d'une conversation comme lus"""
    message.mark_messages_as_read(db, conversation_id, current_user.id)
    return {"status": "success"}

@router.get("/unread-count", response_model=dict)
async def get_unread_messages_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer le nombre de messages non lus"""
    return {"unread_count": message.get_unread_count(db, current_user.id)} 