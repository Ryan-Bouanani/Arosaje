from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.message import Message, Conversation, ConversationParticipant, ConversationType
from schemas.message import MessageCreate, ConversationCreate
from datetime import datetime

class CRUDMessage:
    def create_conversation(
        self,
        db: Session,
        participant_ids: List[int],
        conversation_type: ConversationType,
        related_id: Optional[int] = None,
        initiator_id: Optional[int] = None
    ) -> Conversation:
        """
        Crée une nouvelle conversation avec les participants spécifiés.
        
        Args:
            db: Session de base de données
            participant_ids: Liste des IDs des participants
            conversation_type: Type de la conversation (PLANT_CARE ou BOTANICAL_ADVICE)
            related_id: ID de la garde ou de la demande de conseil associée
            initiator_id: ID de l'utilisateur qui initie la conversation
        """
        # Créer la conversation
        db_conversation = Conversation(
            type=conversation_type,
            related_id=related_id
        )
        db.add(db_conversation)
        db.flush()  # Pour obtenir l'ID de la conversation

        # Ajouter les participants
        for user_id in participant_ids:
            participant = ConversationParticipant(
                conversation_id=db_conversation.id,
                user_id=user_id
            )
            db.add(participant)

        # Si c'est une conversation de type PLANT_CARE, ajouter un message automatique
        if conversation_type == ConversationType.PLANT_CARE and initiator_id:
            message_create = MessageCreate(
                content="La demande de garde a été acceptée. Vous pouvez maintenant discuter des détails.",
                conversation_id=db_conversation.id
            )
            self.create_message(
                db=db,
                message=message_create,
                sender_id=initiator_id
            )

        db.commit()
        db.refresh(db_conversation)
        return db_conversation

    def get_conversation(self, db: Session, conversation_id: int) -> Optional[Conversation]:
        """Récupère une conversation par son ID"""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_user_conversations(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Récupère toutes les conversations d'un utilisateur avec pagination"""
        return (
            db.query(Conversation)
            .join(ConversationParticipant)
            .filter(ConversationParticipant.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_message(self, db: Session, *, message: MessageCreate, sender_id: int) -> Message:
        """Crée un nouveau message"""
        db_message = Message(
            content=message.content,
            conversation_id=message.conversation_id,
            sender_id=sender_id,
            is_read=False
        )
        db.add(db_message)
        
        # Mettre à jour la date de la conversation
        conversation = self.get_conversation(db, message.conversation_id)
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_message)
        return db_message

    def get_conversation_messages(
        self,
        db: Session,
        conversation_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Message]:
        """Récupère les messages d'une conversation avec pagination"""
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def mark_messages_as_read(self, db: Session, conversation_id: int, user_id: int) -> None:
        """Marque tous les messages d'une conversation comme lus pour un utilisateur"""
        # Mettre à jour la date de dernière lecture
        participant = (
            db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id
            )
            .first()
        )
        if participant:
            participant.last_read_at = datetime.utcnow()
            db.commit()

    def get_unread_count(self, db: Session, user_id: int) -> int:
        """Récupère le nombre total de messages non lus pour un utilisateur"""
        return (
            db.query(Message)
            .join(Conversation)
            .join(ConversationParticipant)
            .filter(
                ConversationParticipant.user_id == user_id,
                Message.sender_id != user_id,
                Message.created_at > ConversationParticipant.last_read_at
            )
            .count()
        )

# Créer une instance du CRUD
message = CRUDMessage() 