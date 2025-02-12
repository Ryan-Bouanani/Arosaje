from fastapi import WebSocket
from typing import Dict, Set, Optional
from datetime import datetime
import json
from sqlalchemy.orm import Session
from models.user_status import UserPresence, UserStatus, UserTypingStatus
from models.message import Message
from crud.message import message as message_crud
from crud.user import user as user_crud
from services.email.email_service import EmailService

class ConnectionManager:
    def __init__(self):
        # {user_id: {socket_id: WebSocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        # {conversation_id: set(user_id)}
        self.conversation_participants: Dict[int, Set[int]] = {}
        self.email_service = EmailService()
        
    async def connect(self, websocket: WebSocket, user_id: int, socket_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][socket_id] = websocket

    async def disconnect(self, user_id: int, socket_id: str, db: Session):
        if user_id in self.active_connections:
            if socket_id in self.active_connections[user_id]:
                del self.active_connections[user_id][socket_id]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # Mettre à jour le statut utilisateur
                presence = db.query(UserPresence).filter(UserPresence.user_id == user_id).first()
                if presence:
                    presence.status = UserStatus.OFFLINE
                    presence.last_seen_at = datetime.utcnow()
                    db.commit()

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id].values():
                await websocket.send_json(message)

    async def broadcast_to_conversation(self, message: dict, conversation_id: int, exclude_user_id: Optional[int] = None):
        if conversation_id in self.conversation_participants:
            for user_id in self.conversation_participants[conversation_id]:
                if user_id != exclude_user_id and user_id in self.active_connections:
                    for websocket in self.active_connections[user_id].values():
                        await websocket.send_json(message)

    async def handle_typing_status(self, user_id: int, conversation_id: int, is_typing: bool, db: Session):
        # Mettre à jour le statut de frappe
        typing_status = db.query(UserTypingStatus).filter(
            UserTypingStatus.user_id == user_id,
            UserTypingStatus.conversation_id == conversation_id
        ).first()
        
        if not typing_status:
            typing_status = UserTypingStatus(
                user_id=user_id,
                conversation_id=conversation_id
            )
            db.add(typing_status)
        
        typing_status.is_typing = is_typing
        typing_status.last_typed_at = datetime.utcnow()
        db.commit()

        # Notifier les autres participants
        await self.broadcast_to_conversation(
            {
                "type": "typing_status",
                "user_id": user_id,
                "conversation_id": conversation_id,
                "is_typing": is_typing
            },
            conversation_id,
            exclude_user_id=user_id
        )

    async def handle_message(self, user_id: int, conversation_id: int, content: str, db: Session):
        # Créer le message dans la base de données
        new_message = message_crud.create_message(
            db=db,
            message_in={"content": content, "conversation_id": conversation_id},
            sender_id=user_id
        )

        # Récupérer l'expéditeur pour son nom
        sender = user_crud.get(db, id=user_id)
        sender_name = f"{sender.prenom} {sender.nom}"

        # Notifier tous les participants
        message_data = {
            "type": "new_message",
            "message": {
                "id": new_message.id,
                "content": new_message.content,
                "sender_id": new_message.sender_id,
                "conversation_id": new_message.conversation_id,
                "created_at": new_message.created_at.isoformat(),
                "is_read": new_message.is_read
            }
        }
        
        # Envoyer la notification WebSocket et l'email à chaque participant
        if conversation_id in self.conversation_participants:
            for participant_id in self.conversation_participants[conversation_id]:
                if participant_id != user_id:  # Ne pas envoyer à l'expéditeur
                    # Notification WebSocket
                    if participant_id in self.active_connections:
                        for websocket in self.active_connections[participant_id].values():
                            await websocket.send_json(message_data)
                    
                    # Notification Email
                    participant = user_crud.get(db, id=participant_id)
                    try:
                        await self.email_service.send_new_message_notification(
                            recipient_email=participant.email,
                            sender_name=sender_name,
                            conversation_id=str(conversation_id)
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'envoi de l'email de notification: {e}")

        return new_message

manager = ConnectionManager() 