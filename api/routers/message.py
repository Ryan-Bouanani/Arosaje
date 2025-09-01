from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.security import get_current_user
from utils.rate_limiter import RateLimiter
from crud.message import message
from models.message import ConversationType, Message as MessageModel, ConversationParticipant
from models.user import User as UserModel, UserRole
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
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer une conversation par son ID"""
    if not conversation_id or not conversation_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="L'ID de conversation doit être un nombre entier positif"
        )
    
    conv_id = int(conversation_id)
    conversation = message.get_conversation(db, conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    return conversation

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les messages d'une conversation avec pagination"""
    if not conversation_id or not conversation_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="L'ID de conversation doit être un nombre entier positif"
        )
    
    conv_id = int(conversation_id)
    return message.get_conversation_messages(
        db,
        conversation_id=conv_id,
        skip=skip,
        limit=limit
    )

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def create_message(
    conversation_id: str,
    message_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Envoyer un nouveau message dans une conversation"""
    try:
        if not conversation_id or not conversation_id.isdigit():
            raise HTTPException(
                status_code=400,
                detail="L'ID de conversation doit être un nombre entier positif"
            )
        
        conv_id = int(conversation_id)
        
        # Vérifier le rate limiting
        RateLimiter.check_rate_limit(
            user_id=current_user.id,
            action="send_message",
            max_requests=MESSAGE_RATE_LIMIT,
            time_window=TIME_WINDOW
        )

        message_in.conversation_id = conv_id

        # Vérifier que la conversation existe
        conversation = message.get_conversation(db, conv_id)
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation non trouvée"
            )
        
        # Créer le message
        new_message = message.create_message(
            db=db,
            message=message_in,
            sender_id=current_user.id
        )
        
        # Récupérer les autres participants de la conversation
        participants = message.get_conversation_participants(db, conv_id)
        
        # Envoyer une notification par email à chaque participant (sauf l'expéditeur)
        for participant in participants:
            if participant.id != current_user.id:
                try:
                    await email_service.send_new_message_notification(
                        recipient_email=participant.email,
                        sender_name=f"{current_user.prenom} {current_user.nom}",
                        conversation_id=str(conv_id)
                    )
                except Exception as e:
                    pass  # Ignorer les erreurs d'envoi d'email
        
        return new_message
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur de validation: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la création du message: {str(e)}"
        )

@router.post("/conversations/{conversation_id}/read", response_model=dict)
async def mark_conversation_as_read(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marquer tous les messages d'une conversation comme lus"""
    if not conversation_id or not conversation_id.isdigit():
        raise HTTPException(
            status_code=400,
            detail="L'ID de conversation doit être un nombre entier positif"
        )
    
    conv_id = int(conversation_id)
    message.mark_messages_as_read(db, conv_id, current_user.id)
    return {"status": "success"}

@router.get("/unread-count", response_model=List[Dict[str, int]])
def get_unread_messages_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, int]]:
    """Nombre total de messages non lus de l'utilisateur"""
    try:
        return message.get_unread_count(db, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du comptage des messages non lus"
        )

@router.get("/conversations", response_model=List[Dict[str, Any]])
async def get_user_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste de toutes les conversations de l'utilisateur"""
    try:
        conversations = message.get_user_conversations(
            db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        return conversations
    except Exception as e:
        print(f"Error in get_user_conversations endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des conversations: {str(e)}"
        )

@router.get("/conversations/{conversation_id}/history", response_model=dict)
async def get_conversation_history(
    conversation_id: int,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer l'historique complet d'une conversation avec pagination"""
    total_messages = message.get_conversation_messages_count(db, conversation_id)
    total_pages = (total_messages + page_size - 1) // page_size
    
    messages = message.get_conversation_messages(
        db,
        conversation_id=conversation_id,
        skip=(page - 1) * page_size,
        limit=page_size
    )
    
    return {
        "messages": messages,
        "total_messages": total_messages,
        "current_page": page,
        "total_pages": total_pages,
        "page_size": page_size
    }

@router.get("/conversations/unread", response_model=Dict[str, int])
async def get_unread_messages_by_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer le nombre de messages non lus par conversation"""
    return message.get_unread_count_by_conversation(db, current_user.id)

@router.get("/conversations/{conversation_id}/participants", response_model=List[User])
async def get_conversation_participants(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer la liste des participants d'une conversation"""
    return message.get_conversation_participants(db, conversation_id)

@router.get("/conversations/{conversation_id}/typing", response_model=List[dict])
async def get_typing_users(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer la liste des utilisateurs en train d'écrire"""
    typing_users = message.get_typing_users(db, conversation_id)
    return [
        {
            "user_id": status.user_id,
            "is_typing": status.is_typing,
            "last_typed_at": status.last_typed_at
        }
        for status in typing_users
    ]

@router.post("/{conversation_id}", response_model=Message)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Envoyer un message dans une conversation"""
    # Vérifier que la conversation existe
    conversation = message.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
    
    # Vérifier que l'utilisateur participe à la conversation
    participants = message.get_conversation_participants(db, conversation_id)
    if not any(p.id == current_user.id for p in participants):
        raise HTTPException(status_code=403, detail="Vous ne participez pas à cette conversation")
    
    # Créer le message
    new_message = message.create_message(
        db=db,
        message=message_data,
        sender_id=current_user.id
    )
    
    return new_message

@router.post("/conversations/botanist", response_model=Conversation)
async def create_botanist_conversation(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une conversation avec un botaniste pour une plante"""
    # Stratégie simple : rotation entre les botanistes disponibles
    import random
    
    # Récupérer tous les botanistes
    botanists = db.query(UserModel).filter(UserModel.role == UserRole.BOTANIST).all()
    
    if not botanists:
        raise HTTPException(
            status_code=404,
            detail="Aucun botaniste disponible pour le moment"
        )
    
    # Sélectionner un botaniste de manière équitable (rotation aléatoire)
    botanist = random.choice(botanists)
    
    # Récupérer le nom de la plante
    from crud.plant import plant as plant_crud
    plant = plant_crud.get(db, id=plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plante non trouvée")
    
    # Créer la conversation
    conversation = message.create_conversation(
        db=db,
        participant_ids=[current_user.id, botanist.id],
        conversation_type=ConversationType.BOTANICAL_ADVICE,
        related_id=plant_id,
        initiator_id=current_user.id
    )
    
    # Créer un message automatique d'introduction avec le nom de la plante
    intro_message = message.create_message(
        db=db,
        message=MessageCreate(
            conversation_id=conversation.id,
            content=f"Bonjour, j'aimerais avoir des conseils pour l'entretien de ma plante '{plant.nom}'{f' ({plant.espece})' if plant.espece else ''}. Pouvez-vous m'aider ?"
        ),
        sender_id=current_user.id
    )
    
    return conversation

@router.get("/auth/test")
async def test_auth(
    current_user: User = Depends(get_current_user)
):
    """Endpoint de test pour vérifier l'authentification"""
    return {
        "status": "authenticated", 
        "user_id": current_user.id,
        "user_email": current_user.email,
        "user_role": current_user.role.value if current_user.role else "unknown"
    } 