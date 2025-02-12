from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Optional
import json
import uuid

from utils.database import get_db
from utils.security import get_current_user_ws
from services.websocket.ws_manager import manager
from models.user_status import UserPresence, UserStatus
from crud.message import message as message_crud

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if token is None:
        await websocket.close(code=1008)  # Policy Violation
        return

    # Authentifier l'utilisateur
    try:
        current_user = await get_current_user_ws(token, db)
    except:
        await websocket.close(code=1008)
        return

    # Générer un ID unique pour cette connexion
    socket_id = str(uuid.uuid4())

    try:
        # Accepter la connexion
        await manager.connect(websocket, current_user.id, socket_id)

        # Mettre à jour ou créer le statut de présence
        presence = db.query(UserPresence).filter(UserPresence.user_id == current_user.id).first()
        if not presence:
            presence = UserPresence(user_id=current_user.id)
            db.add(presence)
        
        presence.status = UserStatus.ONLINE
        presence.socket_id = socket_id
        db.commit()

        # Ajouter l'utilisateur aux participants de la conversation
        if conversation_id not in manager.conversation_participants:
            manager.conversation_participants[conversation_id] = set()
        manager.conversation_participants[conversation_id].add(current_user.id)

        try:
            while True:
                data = await websocket.receive_json()
                
                # Gérer les différents types de messages
                message_type = data.get("type")
                
                if message_type == "message":
                    # Envoyer un nouveau message
                    content = data.get("content")
                    if content:
                        await manager.handle_message(
                            user_id=current_user.id,
                            conversation_id=conversation_id,
                            content=content,
                            db=db
                        )

                elif message_type == "typing":
                    # Mettre à jour le statut de frappe
                    is_typing = data.get("is_typing", False)
                    await manager.handle_typing_status(
                        user_id=current_user.id,
                        conversation_id=conversation_id,
                        is_typing=is_typing,
                        db=db
                    )

                elif message_type == "read":
                    # Marquer les messages comme lus
                    message_crud.mark_messages_as_read(
                        db,
                        conversation_id=conversation_id,
                        user_id=current_user.id
                    )
                    # Notifier les autres participants
                    await manager.broadcast_to_conversation(
                        {
                            "type": "messages_read",
                            "user_id": current_user.id,
                            "conversation_id": conversation_id
                        },
                        conversation_id,
                        exclude_user_id=current_user.id
                    )

        except WebSocketDisconnect:
            # Gérer la déconnexion
            if conversation_id in manager.conversation_participants:
                manager.conversation_participants[conversation_id].remove(current_user.id)
                if not manager.conversation_participants[conversation_id]:
                    del manager.conversation_participants[conversation_id]

            await manager.disconnect(current_user.id, socket_id, db)

            # Notifier les autres participants de la déconnexion
            await manager.broadcast_to_conversation(
                {
                    "type": "user_offline",
                    "user_id": current_user.id
                },
                conversation_id,
                exclude_user_id=current_user.id
            )

    except Exception as e:
        print(f"Erreur WebSocket: {e}")
        await websocket.close(code=1011)  # Internal Error 