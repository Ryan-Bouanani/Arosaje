from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.message import (
    Message,
    Conversation,
    ConversationParticipant,
    ConversationType,
)
from schemas.message import MessageCreate
from datetime import datetime, timedelta, timezone
from models.user import User
from models.user_status import UserTypingStatus
from models.plant import Plant
from models.plant_care import PlantCare


class CRUDMessage:
    def create_conversation(
        self,
        db: Session,
        participant_ids: List[int],
        conversation_type: ConversationType,
        related_id: Optional[int] = None,
        initiator_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Crée une nouvelle conversation avec les participants spécifiés, ou retourne une conversation existante."""
        import logging
        import time

        logger = logging.getLogger(__name__)
        start_time = time.time()

        logger.info(f"🔵 CRUD create_conversation: DEBUT")
        logger.info(f"🔵 CRUD create_conversation: participant_ids={participant_ids}")
        logger.info(f"🔵 CRUD create_conversation: type={conversation_type}, related_id={related_id}")

        # Vérifier s'il existe déjà une conversation avec les mêmes paramètres
        if conversation_type == ConversationType.PLANT_CARE and related_id:
            check_start = time.time()
            existing_conversation = self._find_existing_plant_care_conversation(db, participant_ids, related_id)
            check_duration = (time.time() - check_start) * 1000
            logger.info(f"🔵 CRUD: Vérification conversation existante: {check_duration:.2f}ms")

            if existing_conversation:
                total_duration = (time.time() - start_time) * 1000
                logger.info(f"🔵 CRUD: Conversation existante trouvée en {total_duration:.2f}ms")
                return existing_conversation

        logger.info(f"🔵 CRUD: Création nouvelle conversation...")
        db_conversation = Conversation(type=conversation_type, related_id=related_id)
        db.add(db_conversation)

        flush_start = time.time()
        db.flush()
        flush_duration = (time.time() - flush_start) * 1000
        logger.info(f"🔵 CRUD: db.flush() en {flush_duration:.2f}ms - conversation_id={db_conversation.id}")

        logger.info(f"🔵 CRUD: Ajout des participants...")
        for i, user_id in enumerate(participant_ids):
            participant = ConversationParticipant(
                conversation_id=db_conversation.id, user_id=user_id
            )
            db.add(participant)
            logger.info(f"🔵 CRUD: Participant {i+1}/{len(participant_ids)} ajouté (user_id={user_id})")

        commit_start = time.time()
        db.commit()
        commit_duration = (time.time() - commit_start) * 1000
        logger.info(f"🔵 CRUD: db.commit() en {commit_duration:.2f}ms")

        db.refresh(db_conversation)

        # Utiliser la méthode commune pour construire la réponse
        response_start = time.time()
        result = self._build_conversation_response(db, db_conversation)
        response_duration = (time.time() - response_start) * 1000

        total_duration = (time.time() - start_time) * 1000
        logger.info(f"🔵 CRUD: _build_conversation_response en {response_duration:.2f}ms")
        logger.info(f"🔵 CRUD create_conversation: SUCCESS total {total_duration:.2f}ms")
        logger.info(f"🔵 CRUD: result participants={[p.get('user', {}).get('id') for p in result.get('participants', [])]}")

        return result

    def _find_existing_plant_care_conversation(
        self, db: Session, participant_ids: List[int], related_id: int
    ) -> Optional[Dict[str, Any]]:
        """Cherche une conversation existante pour une garde de plante entre les mêmes participants."""
        
        # Rechercher les conversations de type plant_care avec le même related_id
        conversations = (
            db.query(Conversation)
            .filter(
                Conversation.type == ConversationType.PLANT_CARE,
                Conversation.related_id == related_id
            )
            .all()
        )
        
        # Vérifier si l'une des conversations a exactement les mêmes participants
        for conv in conversations:
            conv_participant_ids = [
                p.user_id for p in db.query(ConversationParticipant)
                .filter(ConversationParticipant.conversation_id == conv.id)
                .all()
            ]
            
            # Comparer les listes de participants (ordre non important)
            if set(conv_participant_ids) == set(participant_ids):
                # Construire la réponse complète pour cette conversation existante
                return self._build_conversation_response(db, conv)
        
        return None

    def _build_conversation_response(
        self, db: Session, conversation: Conversation
    ) -> Dict[str, Any]:
        """Construit la réponse complète pour une conversation."""
        
        conv_dict = {
            "id": conversation.id,
            "type": conversation.type.value if conversation.type else "plant_care",
            "related_id": conversation.related_id,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "unread_count": 0,
            "last_message": None,
            "participants": [],
            "plant_info": None,
            "plant_care_info": None,
        }

        # Récupérer les participants avec leurs détails
        participants = (
            db.query(User)
            .join(ConversationParticipant)
            .filter(ConversationParticipant.conversation_id == conversation.id)
            .all()
        )

        # Ajouter les informations des participants
        for participant in participants:
            conv_dict["participants"].append({
                "id": participant.id,
                "user_id": participant.id,  # Pour compatibilité
                "last_name": participant.last_name,
                "first_name": participant.first_name,
                "email": participant.email,
            })

        # Si c'est une conversation de type plant_care, récupérer les infos de la plante
        if (
            conversation.type
            and conversation.type.value == "plant_care"
            and conversation.related_id
        ):
            # Récupérer la garde de plante
            plant_care = (
                db.query(PlantCare)
                .filter(PlantCare.id == conversation.related_id)
                .first()
            )
            if plant_care:
                # Récupérer la plante
                plant = (
                    db.query(Plant)
                    .filter(Plant.id == plant_care.plant_id)
                    .first()
                )
                if plant:
                    conv_dict["plant_info"] = {
                        "id": plant.id,
                        "name": plant.name,
                        "species": plant.species,
                    }

                conv_dict["plant_care_info"] = {
                    "id": plant_care.id,
                    "start_date": plant_care.start_date.isoformat(),
                    "end_date": plant_care.end_date.isoformat(),
                    "owner_id": plant_care.owner_id,
                    "caretaker_id": plant_care.caretaker_id,
                }

        return conv_dict

    def get_conversation(
        self, db: Session, conversation_id: int
    ) -> Optional[Conversation]:
        """Récupère une conversation par son ID"""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_user_conversations(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Récupère toutes les conversations d'un utilisateur avec leurs détails"""
        try:

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

            result = []
            for i, conversation in enumerate(conversations):
                print(
                    f"DEBUG: Processing conversation {i+1}/{len(conversations)}: id={conversation.id}, type={conversation.type}"
                )
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
                    .join(
                        ConversationParticipant,
                        ConversationParticipant.conversation_id
                        == Message.conversation_id,
                    )
                    .filter(
                        ConversationParticipant.user_id == user_id,
                        Message.conversation_id == conversation.id,
                        Message.sender_id != user_id,
                        Message.sender_id.isnot(None),
                        not Message.is_read,
                        (
                            (ConversationParticipant.last_read_at.is_(None))
                            | (
                                Message.created_at
                                > ConversationParticipant.last_read_at
                            )
                        ),
                    )
                    .count()
                )

                # Récupérer les participants (pour obtenir l'autre personne)
                participants = (
                    db.query(User)
                    .join(ConversationParticipant)
                    .filter(
                        ConversationParticipant.conversation_id == conversation.id
                    )
                    .all()
                )

                # Construire le dictionnaire de la conversation
                conv_dict = {
                    "id": conversation.id,
                    "type": (
                        conversation.type.value if conversation.type else "plant_care"
                    ),
                    "related_id": conversation.related_id,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                    "unread_count": unread_count,
                    "last_message": None,
                    "participants": [],
                    "plant_info": None,
                    "plant_care_info": None,
                }

                # Ajouter les informations des participants
                for participant in participants:
                    conv_dict["participants"].append(
                        {
                            "id": participant.id,
                            "user_id": participant.id,  # Pour compatibilité Flutter
                            "last_name": participant.last_name,
                            "first_name": participant.first_name,
                            "email": participant.email,
                        }
                    )

                # Si c'est une conversation de type plant_care, récupérer les infos de la plante
                if (
                    conversation.type
                    and conversation.type.value == "plant_care"
                    and conversation.related_id
                ):
                    # Récupérer la garde de plante
                    plant_care = (
                        db.query(PlantCare)
                        .filter(PlantCare.id == conversation.related_id)
                        .first()
                    )
                    if plant_care:
                        # Récupérer la plante
                        plant = (
                            db.query(Plant)
                            .filter(Plant.id == plant_care.plant_id)
                            .first()
                        )
                        if plant:
                            conv_dict["plant_info"] = {
                                "id": plant.id,
                                "name": plant.name,
                                "species": plant.species,
                            }

                        conv_dict["plant_care_info"] = {
                            "id": plant_care.id,
                            "start_date": plant_care.start_date.isoformat(),
                            "end_date": plant_care.end_date.isoformat(),
                            "owner_id": plant_care.owner_id,
                            "caretaker_id": plant_care.caretaker_id,
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
                        "is_read": last_message.is_read,
                    }
                    print(
                        f"DEBUG: Added last message for conversation {conversation.id}: '{last_message.content}'"
                    )

                result.append(conv_dict)

            if result and len(result) > 0 and result[0] is not None:
                first_conv = result[0]
                if isinstance(first_conv, dict) and "id" in first_conv:
                    last_msg_content = "No message"
                    if first_conv.get("last_message") and isinstance(
                        first_conv["last_message"], dict
                    ):
                        last_msg_content = first_conv["last_message"].get(
                            "content", "No message"
                        )
                    print(
                        f"DEBUG: First conversation: {first_conv['id']} - {last_msg_content}"
                    )
                else:
                    print(f"DEBUG: First conversation is invalid: {type(first_conv)}")

            return result

        except Exception as e:
            print(f"Error in get_user_conversations: {e}")
            raise

    def create_message(
        self, db: Session, *, message: MessageCreate, sender_id: Optional[int] = None
    ) -> Message:
        """Crée un nouveau message"""
        try:
            db_message = Message(
                content=message.content,
                conversation_id=message.conversation_id,
                sender_id=sender_id,
                is_read=False,
            )
            db.add(db_message)

            conversation = self.get_conversation(db, message.conversation_id)
            if not conversation:
                raise ValueError("Conversation non trouvée")

            conversation.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(db_message)

            if not db_message.id:
                raise ValueError("Le message n'a pas été créé correctement")

            return db_message

        except Exception as e:
            db.rollback()
            raise ValueError(f"Erreur lors de la création du message: {str(e)}")

    def get_conversation_messages(
        self, db: Session, conversation_id: int, skip: int = 0, limit: int = 50
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

        except Exception:
            raise

    def mark_messages_as_read(
        self, db: Session, conversation_id: int, user_id: int
    ) -> None:
        """Marque tous les messages d'une conversation comme lus pour un utilisateur"""
        try:
            db.query(Message).filter(
                Message.conversation_id == conversation_id, not Message.is_read
            ).update({"is_read": True})

            participant = (
                db.query(ConversationParticipant)
                .filter(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == user_id,
                )
                .first()
            )
            if participant:
                participant.last_read_at = datetime.now(timezone.utc)

            db.commit()

        except Exception:
            db.rollback()
            raise

    def get_unread_count(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Récupère le nombre total de messages non lus pour un utilisateur"""
        try:
            unread_query = (
                db.query(Message.conversation_id, func.count(Message.id).label("count"))
                .join(
                    ConversationParticipant,
                    ConversationParticipant.conversation_id == Message.conversation_id,
                )
                .filter(
                    ConversationParticipant.user_id == user_id,
                    Message.sender_id != user_id,
                    Message.sender_id.isnot(None),
                    not Message.is_read,
                    (
                        (ConversationParticipant.last_read_at.is_(None))
                        | (Message.created_at > ConversationParticipant.last_read_at)
                    ),
                )
                .group_by(Message.conversation_id)
            )

            unread_messages = unread_query.all()

            result = []
            for conversation_id, count in unread_messages:
                if count > 0:
                    result.append(
                        {
                            "conversation_id": int(conversation_id),
                            "unread_count": int(count),
                        }
                    )

            if not result:
                result.append({"conversation_id": 0, "unread_count": 0})

            return result

        except Exception:
            return [{"conversation_id": 0, "unread_count": 0}]

    def get_conversation_messages_count(self, db: Session, conversation_id: int) -> int:
        """Compte le nombre total de messages dans une conversation"""
        return (
            db.query(Message).filter(Message.conversation_id == conversation_id).count()
        )

    def get_unread_count_by_conversation(
        self, db: Session, user_id: int
    ) -> List[Dict[str, Any]]:
        """Compte les messages non lus par conversation"""
        try:
            unread_messages = (
                db.query(
                    Message.conversation_id, db.func.count(Message.id).label("count")
                )
                .join(
                    ConversationParticipant,
                    ConversationParticipant.conversation_id == Message.conversation_id,
                )
                .filter(
                    ConversationParticipant.user_id == user_id,
                    Message.sender_id != user_id,
                    (
                        (ConversationParticipant.last_read_at.is_(None))
                        | (Message.created_at > ConversationParticipant.last_read_at)
                    ),
                )
                .group_by(Message.conversation_id)
                .all()
            )

            result = []
            for conversation_id, count in unread_messages:
                if conversation_id is not None and count is not None:
                    try:
                        result.append(
                            {
                                "conversation_id": int(conversation_id),
                                "unread_count": int(count),
                            }
                        )
                    except (ValueError, TypeError):
                        continue

            if not result:
                result.append({"conversation_id": 0, "unread_count": 0})

            return result

        except Exception:
            return [{"conversation_id": 0, "unread_count": 0}]

    def get_conversation_participants(
        self, db: Session, conversation_id: int
    ) -> List[User]:
        """Récupère la liste des participants d'une conversation"""
        return (
            db.query(User)
            .join(ConversationParticipant)
            .filter(ConversationParticipant.conversation_id == conversation_id)
            .all()
        )

    def get_typing_users(
        self, db: Session, conversation_id: int
    ) -> List[UserTypingStatus]:
        """Récupère la liste des utilisateurs en train d'écrire"""
        thirty_seconds_ago = datetime.now(timezone.utc) - timedelta(seconds=30)
        return (
            db.query(UserTypingStatus)
            .filter(
                UserTypingStatus.conversation_id == conversation_id,
                UserTypingStatus.is_typing,
                UserTypingStatus.last_typed_at >= thirty_seconds_ago,
            )
            .all()
        )


# Créer une instance du CRUD
message = CRUDMessage()
