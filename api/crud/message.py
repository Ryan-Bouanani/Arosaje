from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from models.message import Message, Conversation, ConversationParticipant, ConversationType
from schemas.message import MessageCreate, ConversationCreate
from datetime import datetime, timedelta
from models.user import User
from models.user_status import UserTypingStatus, UserPresence, UserStatus
from models.plant import Plant
from models.plant_care import PlantCare

class CRUDMessage:
    def create_conversation(
        self,
        db: Session,
        participant_ids: List[int],
        conversation_type: ConversationType,
        related_id: Optional[int] = None,
        initiator_id: Optional[int] = None
    ) -> Conversation:
        """Crée une nouvelle conversation avec les participants spécifiés."""
        db_conversation = Conversation(
            type=conversation_type,
            related_id=related_id
        )
        db.add(db_conversation)
        db.flush()

        for user_id in participant_ids:
            participant = ConversationParticipant(
                conversation_id=db_conversation.id,
                user_id=user_id
            )
            db.add(participant)

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
    ) -> List[Dict[str, Any]]:
        """Récupère toutes les conversations d'un utilisateur avec leurs détails"""
        try:
            print(f"DEBUG: Getting conversations for user_id={user_id}, skip={skip}, limit={limit}")
            
            # Récupérer les conversations de l'utilisateur
            conversations = (
                db.query(Conversation)
                .join(ConversationParticipant)
                .filter(ConversationParticipant.user_id == user_id)
                .order_by(Conversation.updated_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            print(f"DEBUG: Found {len(conversations)} conversations for user {user_id}")
            
            result = []
            for i, conversation in enumerate(conversations):
                print(f"DEBUG: Processing conversation {i+1}/{len(conversations)}: id={conversation.id}, type={conversation.type}")
                # Récupérer le dernier message
                last_message = (
                    db.query(Message)
                    .filter(Message.conversation_id == conversation.id)
                    .order_by(Message.created_at.desc())
                    .first()
                )
                
                # Compter les messages non lus pour cette conversation
                unread_count = (
                    db.query(Message)
                    .join(ConversationParticipant, ConversationParticipant.conversation_id == Message.conversation_id)
                    .filter(
                        ConversationParticipant.user_id == user_id,
                        Message.conversation_id == conversation.id,
                        Message.sender_id != user_id,
                        Message.sender_id.isnot(None),
                        Message.is_read == False,
                        (
                            (ConversationParticipant.last_read_at.is_(None)) |
                            (Message.created_at > ConversationParticipant.last_read_at)
                        )
                    )
                    .count()
                )
                
                # Récupérer les participants (pour obtenir l'autre personne)
                participants = (
                    db.query(User)
                    .join(ConversationParticipant)
                    .filter(
                        ConversationParticipant.conversation_id == conversation.id,
                        ConversationParticipant.user_id != user_id  # Exclure l'utilisateur actuel
                    )
                    .all()
                )
                
                # Construire le dictionnaire de la conversation
                conv_dict = {
                    "id": conversation.id,
                    "type": conversation.type.value if conversation.type else "plant_care",
                    "related_id": conversation.related_id,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                    "unread_count": unread_count,
                    "last_message": None,
                    "participants": [],
                    "plant_info": None,
                    "plant_care_info": None
                }
                
                # Ajouter les informations des participants
                for participant in participants:
                    conv_dict["participants"].append({
                        "id": participant.id,
                        "nom": participant.nom,
                        "prenom": participant.prenom,
                        "email": participant.email
                    })
                
                # Si c'est une conversation de type plant_care, récupérer les infos de la plante
                if conversation.type.value == "plant_care" and conversation.related_id:
                    # Récupérer la garde de plante
                    plant_care = db.query(PlantCare).filter(PlantCare.id == conversation.related_id).first()
                    if plant_care:
                        # Récupérer la plante
                        plant = db.query(Plant).filter(Plant.id == plant_care.plant_id).first()
                        if plant:
                            conv_dict["plant_info"] = {
                                "id": plant.id,
                                "nom": plant.nom,
                                "espece": plant.espece
                            }
                        
                        conv_dict["plant_care_info"] = {
                            "id": plant_care.id,
                            "start_date": plant_care.start_date.isoformat(),
                            "end_date": plant_care.end_date.isoformat(),
                            "owner_id": plant_care.owner_id,
                            "caretaker_id": plant_care.caretaker_id
                        }
                
                # Ajouter le dernier message s'il existe
                if last_message:
                    conv_dict["last_message"] = {
                        "id": last_message.id,
                        "content": last_message.content,
                        "sender_id": last_message.sender_id,
                        "conversation_id": last_message.conversation_id,
                        "created_at": last_message.created_at.isoformat(),
                        "updated_at": last_message.updated_at.isoformat(),
                        "is_read": last_message.is_read
                    }
                    print(f"DEBUG: Added last message for conversation {conversation.id}: '{last_message.content}'")
                
                result.append(conv_dict)
            
            print(f"DEBUG: Returning {len(result)} conversations")
            if result:
                print(f"DEBUG: First conversation: {result[0]['id']} - {result[0].get('last_message', {}).get('content', 'No message')}")
            
            return result
            
        except Exception as e:
            print(f"Error in get_user_conversations: {e}")
            raise

    def create_message(self, db: Session, *, message: MessageCreate, sender_id: Optional[int] = None) -> Message:
        """Crée un nouveau message"""
        try:
            db_message = Message(
                content=message.content,
                conversation_id=message.conversation_id,
                sender_id=sender_id,
                is_read=False
            )
            db.add(db_message)
            
            conversation = self.get_conversation(db, message.conversation_id)
            if not conversation:
                raise ValueError("Conversation non trouvée")
            
            conversation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_message)
            
            if not db_message.id:
                raise ValueError("Le message n'a pas été créé correctement")
            
            return db_message
            
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erreur lors de la création du message: {str(e)}")

    def get_conversation_messages(
        self,
        db: Session,
        conversation_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Récupère les messages d'une conversation avec pagination"""
        try:
            conversation = self.get_conversation(db, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} non trouvée")

            messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            result = []
            for message in messages:
                msg_dict = message.to_dict()
                msg_dict["id"] = int(float(msg_dict["id"]))
                msg_dict["conversation_id"] = int(float(msg_dict["conversation_id"]))
                if msg_dict["sender_id"]:
                    msg_dict["sender_id"] = int(float(msg_dict["sender_id"]))
                result.append(msg_dict)
            
            return result
            
        except Exception as e:
            raise

    def mark_messages_as_read(self, db: Session, conversation_id: int, user_id: int) -> None:
        """Marque tous les messages d'une conversation comme lus pour un utilisateur"""
        try:
            db.query(Message)\
                .filter(
                    Message.conversation_id == conversation_id,
                    Message.is_read == False
                )\
                .update({"is_read": True})

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
            
        except Exception as e:
            db.rollback()
            raise

    def get_unread_count(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Récupère le nombre total de messages non lus pour un utilisateur"""
        try:
            unread_query = (
                db.query(Message.conversation_id, func.count(Message.id).label('count'))
                .join(ConversationParticipant, ConversationParticipant.conversation_id == Message.conversation_id)
                .filter(
                    ConversationParticipant.user_id == user_id,
                    Message.sender_id != user_id,
                    Message.sender_id.isnot(None),
                    Message.is_read == False,
                    (
                        (ConversationParticipant.last_read_at.is_(None)) |
                        (Message.created_at > ConversationParticipant.last_read_at)
                    )
                )
                .group_by(Message.conversation_id)
            )
            
            unread_messages = unread_query.all()
            
            result = []
            for conversation_id, count in unread_messages:
                if count > 0:
                    result.append({
                        "conversation_id": int(conversation_id),
                        "unread_count": int(count)
                    })
            
            if not result:
                result.append({
                    "conversation_id": 0,
                    "unread_count": 0
                })
            
            return result
            
        except Exception as e:
            return [{"conversation_id": 0, "unread_count": 0}]

    def get_conversation_messages_count(self, db: Session, conversation_id: int) -> int:
        """Compte le nombre total de messages dans une conversation"""
        return db.query(Message)\
            .filter(Message.conversation_id == conversation_id)\
            .count()

    def get_unread_count_by_conversation(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Compte les messages non lus par conversation"""
        try:
            unread_messages = (
                db.query(Message.conversation_id, db.func.count(Message.id).label('count'))
                .join(ConversationParticipant, ConversationParticipant.conversation_id == Message.conversation_id)
                .filter(
                    ConversationParticipant.user_id == user_id,
                    Message.sender_id != user_id,
                    (
                        (ConversationParticipant.last_read_at.is_(None)) |
                        (Message.created_at > ConversationParticipant.last_read_at)
                    )
                )
                .group_by(Message.conversation_id)
                .all()
            )
            
            result = []
            for conversation_id, count in unread_messages:
                if conversation_id is not None and count is not None:
                    try:
                        result.append({
                            "conversation_id": int(conversation_id),
                            "unread_count": int(count)
                        })
                    except (ValueError, TypeError):
                        continue
            
            if not result:
                result.append({
                    "conversation_id": 0,
                    "unread_count": 0
                })
                
            return result
            
        except Exception as e:
            return [{"conversation_id": 0, "unread_count": 0}]

    def get_conversation_participants(self, db: Session, conversation_id: int) -> List[User]:
        """Récupère la liste des participants d'une conversation"""
        return db.query(User)\
            .join(ConversationParticipant)\
            .filter(ConversationParticipant.conversation_id == conversation_id)\
            .all()

    def get_typing_users(self, db: Session, conversation_id: int) -> List[UserTypingStatus]:
        """Récupère la liste des utilisateurs en train d'écrire"""
        thirty_seconds_ago = datetime.utcnow() - timedelta(seconds=30)
        return db.query(UserTypingStatus)\
            .filter(
                UserTypingStatus.conversation_id == conversation_id,
                UserTypingStatus.is_typing == True,
                UserTypingStatus.last_typed_at >= thirty_seconds_ago
            )\
            .all()

# Créer une instance du CRUD
message = CRUDMessage() 