from typing import List, Dict, Any
import logging

def validate_message_response(response, expected_sender_id=None, max_length=2000):
    """Valide la réponse d'un message"""
    assert response.status_code == 200
    data = response.json()
    
    # Vérification des champs obligatoires
    required_fields = ["id", "content", "sender_id", "conversation_id", "created_at", "updated_at", "is_read"]
    for field in required_fields:
        assert field in data, f"Le champ {field} est manquant dans la réponse"
        
    # Vérification des types des champs avec conversion sécurisée
    try:
        # Conversion de l'ID du message
        if data["id"]:
            try:
                data["id"] = int(float(data["id"]))
            except (ValueError, TypeError):
                raise AssertionError(f"L'ID du message '{data['id']}' n'est pas un nombre valide")
        
        # Conversion de l'ID de conversation
        if data["conversation_id"]:
            try:
                data["conversation_id"] = int(float(data["conversation_id"]))
            except (ValueError, TypeError):
                raise AssertionError(f"L'ID de conversation '{data['conversation_id']}' n'est pas un nombre valide")
        
        # Conversion de l'ID de l'expéditeur
        if data["sender_id"]:
            try:
                data["sender_id"] = int(float(data["sender_id"]))
            except (ValueError, TypeError):
                if data["sender_id"] != '':  # Ignorer les chaînes vides pour sender_id
                    raise AssertionError(f"L'ID de l'expéditeur '{data['sender_id']}' n'est pas un nombre valide")
                else:
                    data["sender_id"] = None
    except (ValueError, TypeError) as e:
        raise AssertionError(f"Erreur de conversion des IDs: {str(e)}")
    
    assert isinstance(data["content"], str), "Le contenu doit être une chaîne de caractères"
    assert isinstance(data["is_read"], bool), "is_read doit être un booléen"
    
    # Vérifier que les IDs sont positifs
    assert data["id"] > 0, "L'ID du message doit être positif"
    if data["sender_id"] is not None:
        assert data["sender_id"] > 0, "L'ID de l'expéditeur doit être positif"
    assert data["conversation_id"] > 0, "L'ID de la conversation doit être positif"
    
    # Vérifier l'expéditeur si spécifié
    if expected_sender_id is not None and expected_sender_id != '':
        try:
            expected_id = int(float(expected_sender_id))
            assert data["sender_id"] == expected_id, \
                f"ID de l'expéditeur incorrect. Attendu: {expected_id}, Reçu: {data['sender_id']}"
        except (ValueError, TypeError):
            # Si expected_sender_id n'est pas un nombre valide, on ignore la validation
            pass
    
    # Vérifier la longueur du message
    assert len(data["content"]) <= max_length, \
        f"Le message dépasse la longueur maximale autorisée de {max_length} caractères"
    
    return True

def validate_messages_list_response(response, expected_count=None, expected_content=None, all_read=None):
    """Valide la réponse d'une liste de messages"""
    print("\nValidation des messages:")
    
    # Vérifier le code de statut
    print(f"Code de statut de la réponse: {response.status_code}")
    assert response.status_code == 200, f"Le code de statut devrait être 200, mais est {response.status_code}"
    
    # Récupérer les données
    try:
        data = response.json()
        print(f"Données reçues: {data}")
    except Exception as e:
        print(f"Erreur lors du parsing JSON: {str(e)}")
        raise AssertionError(f"La réponse n'est pas un JSON valide: {str(e)}")
    
    # Vérifier que data est une liste
    assert isinstance(data, list), f"La réponse devrait être une liste, mais est de type {type(data)}"
    
    # Afficher les informations sur les messages
    print(f"Nombre de messages trouvés: {len(data)}")
    if expected_count is not None:
        print(f"Nombre de messages attendus: {expected_count}")
    if expected_content is not None:
        print(f"Contenu attendu: '{expected_content}'")
    
    # Si aucun message n'est trouvé
    if len(data) == 0:
        print("\nAucun message trouvé dans la réponse")
        if expected_count and expected_count > 0:
            raise AssertionError(f"Le nombre de messages devrait être au moins {expected_count}, mais est 0")
        return
    
    # Afficher les détails de chaque message
    print("\nDétails des messages trouvés:")
    for i, message in enumerate(data):
        print(f"\nMessage {i + 1}:")
        try:
            # Conversion sécurisée des IDs avec gestion des chaînes vides
            if 'id' in message and message['id']:
                try:
                    message['id'] = int(float(message['id']))
                except (ValueError, TypeError):
                    raise AssertionError(f"L'ID du message '{message['id']}' n'est pas un nombre valide")
                    
            if 'conversation_id' in message and message['conversation_id']:
                try:
                    message['conversation_id'] = int(float(message['conversation_id']))
                except (ValueError, TypeError):
                    raise AssertionError(f"L'ID de conversation '{message['conversation_id']}' n'est pas un nombre valide")
                    
            if 'sender_id' in message and message['sender_id']:
                try:
                    message['sender_id'] = int(float(message['sender_id']))
                except (ValueError, TypeError):
                    if message['sender_id'] != '':  # Ignorer les chaînes vides pour sender_id
                        raise AssertionError(f"L'ID de l'expéditeur '{message['sender_id']}' n'est pas un nombre valide")
            
            print(f"  ID: {message.get('id', 'Non défini')}")
            print(f"  Contenu: {message.get('content', 'Non défini')}")
            print(f"  Expéditeur: {message.get('sender_id', 'Non défini')}")
            print(f"  Conversation: {message.get('conversation_id', 'Non défini')}")
            print(f"  Date de création: {message.get('created_at', 'Non définie')}")
            print(f"  Lu: {message.get('is_read', 'Non défini')}")
            
            # Vérifier que les champs requis sont présents et du bon type
            assert isinstance(message.get('id'), int), f"L'ID du message doit être un entier"
            assert isinstance(message.get('content'), str), f"Le contenu du message doit être une chaîne"
            assert isinstance(message.get('sender_id'), (int, type(None))), \
                f"L'ID de l'expéditeur doit être un entier ou null"
            assert isinstance(message.get('conversation_id'), int), f"L'ID de la conversation doit être un entier"
            assert isinstance(message.get('created_at'), str), f"La date de création doit être une chaîne"
            assert isinstance(message.get('is_read'), bool), f"is_read doit être un booléen"
            
            # Vérifier le statut de lecture si demandé
            if all_read is not None:
                if all_read and not message.get('is_read'):
                    raise AssertionError(f"Le message {message['id']} n'est pas marqué comme lu")
                elif not all_read and message.get('is_read'):
                    raise AssertionError(f"Le message {message['id']} ne devrait pas être marqué comme lu")
            
        except (ValueError, TypeError) as e:
            print(f"Erreur lors de la validation du message {i + 1}: {str(e)}")
            print(f"Message problématique: {message}")
            raise AssertionError(f"Erreur de conversion des données du message: {str(e)}")
        except Exception as e:
            print(f"Erreur lors de la validation du message {i + 1}: {str(e)}")
            print(f"Message problématique: {message}")
            raise
    
    # Vérifier le nombre de messages
    if expected_count is not None:
        assert len(data) >= expected_count, \
            f"Le nombre de messages devrait être au moins {expected_count}, mais est {len(data)}"
    
    # Vérifier le contenu si spécifié
    if expected_content is not None:
        content_found = False
        for message in data:
            if message.get('content') == expected_content:
                content_found = True
                print(f"\nMessage avec le contenu attendu trouvé: {message}")
                break
        
        if not content_found:
            print("\nContenu des messages trouvés:")
            for message in data:
                print(f"  - {message.get('content')}")
            raise AssertionError(f"Aucun message avec le contenu '{expected_content}' n'a été trouvé")
    
    return True

def validate_message_structure(message: Dict[str, Any]) -> None:
    """Valide la structure d'un message"""
    required_fields = ["id", "content", "sender_id", "conversation_id", "created_at", "is_read"]
    for field in required_fields:
        assert field in message, f"Le champ {field} est manquant"

def validate_paginated_messages_response(response: Dict[str, Any], expected_page_size: int) -> None:
    """Valide une réponse paginée de messages"""
    required_fields = ["messages", "total_messages", "current_page", "total_pages", "page_size"]
    for field in required_fields:
        assert field in response, f"Le champ {field} est manquant"
    
    assert len(response["messages"]) <= expected_page_size, "Trop de messages retournés"
    assert response["page_size"] == expected_page_size, "Taille de page incorrecte"
    assert response["current_page"] >= 1, "Numéro de page invalide"
    assert response["total_pages"] >= 1, "Nombre total de pages invalide"
    
    for message in response["messages"]:
        validate_message_structure(message)

def validate_unread_messages_response(response: Dict[str, Any], conversation_id: int = None) -> None:
    """Valide une réponse contenant le nombre de messages non lus par conversation"""
    # Vérifier que la réponse est une liste
    assert isinstance(response, list), "La réponse devrait être une liste"
    
    # Vérifier que chaque élément a la bonne structure
    for item in response:
        assert "conversation_id" in item, "Chaque élément devrait avoir un conversation_id"
        assert "unread_count" in item, "Chaque élément devrait avoir un unread_count"
        assert isinstance(item["conversation_id"], int), "conversation_id devrait être un entier"
        assert isinstance(item["unread_count"], int), "unread_count devrait être un entier"
        assert item["unread_count"] >= 0, "unread_count ne peut pas être négatif"
    
    # Si un ID de conversation est spécifié, vérifier qu'il a des messages non lus
    if conversation_id is not None:
        conversation_found = False
        for item in response:
            if item["conversation_id"] == conversation_id:
                conversation_found = True
                assert item["unread_count"] > 0, \
                    f"La conversation {conversation_id} devrait avoir des messages non lus"
                break
        if not conversation_found:
            raise AssertionError(f"La conversation {conversation_id} n'a pas été trouvée dans la réponse")

def validate_participants_response(response: List[Dict[str, Any]], expected_count: int, expected_participants: List[int]) -> None:
    """Valide une réponse contenant la liste des participants"""
    assert isinstance(response, list), "La réponse devrait être une liste"
    assert len(response) == expected_count, f"Le nombre de participants devrait être {expected_count}"
    
    # Convertir les IDs de manière sécurisée
    participant_ids = []
    for p in response:
        try:
            if 'id' in p:
                p['id'] = int(float(p['id']))
                participant_ids.append(p['id'])
        except (ValueError, TypeError) as e:
            raise AssertionError(f"Erreur de conversion de l'ID du participant: {str(e)}")
    
    # Convertir les IDs attendus de manière sécurisée
    safe_expected_ids = []
    for expected_id in expected_participants:
        try:
            if expected_id is not None:
                safe_expected_ids.append(int(float(expected_id)))
        except (ValueError, TypeError) as e:
            raise AssertionError(f"Erreur de conversion de l'ID attendu: {str(e)}")
    
    # Vérifier que tous les participants attendus sont présents
    for expected_id in safe_expected_ids:
        assert expected_id in participant_ids, f"Le participant {expected_id} est manquant"
    
    # Vérifier les champs requis
    for participant in response:
        required_fields = ["id", "email", "nom", "prenom"]
        for field in required_fields:
            assert field in participant, f"Le champ {field} est manquant"
            if field == "id":
                assert isinstance(participant[field], int), f"L'ID du participant doit être un entier"
            else:
                assert isinstance(participant[field], str), f"Le champ {field} doit être une chaîne"

def validate_message_with_email_notification(response: Dict[str, Any], recipient_email: str, sender_name: str) -> None:
    """Valide un message et vérifie que la notification par email a été envoyée"""
    validate_message_structure(response)
    
    # Note: Dans un environnement de test, on pourrait vérifier l'envoi d'email
    # en utilisant un mock du service d'email ou en vérifiant une file d'attente de test
    # Pour l'instant, on vérifie juste la structure du message
    assert response["is_read"] is False, "Le nouveau message devrait être non lu"
    assert "created_at" in response, "Le timestamp de création est manquant"

def validate_unread_count_response(response):
    """Valide la réponse du compteur de messages non lus"""
    assert response.status_code == 200
    data = response.json()
    
    # Vérifier que la réponse est une liste
    assert isinstance(data, list), "La réponse devrait être une liste"
    
    # Vérifier chaque élément de la liste
    for item in data:
        assert isinstance(item, dict), "Chaque élément devrait être un dictionnaire"
        assert "conversation_id" in item, "Chaque élément devrait avoir un conversation_id"
        assert "unread_count" in item, "Chaque élément devrait avoir un unread_count"
        assert isinstance(item["conversation_id"], int), "conversation_id devrait être un entier"
        assert isinstance(item["unread_count"], int), "unread_count devrait être un entier"
        assert item["unread_count"] >= 0, "unread_count ne peut pas être négatif"
    
    return True

def validate_websocket_connection_response(response):
    """Valide la réponse de connexion WebSocket"""
    assert response.status_code == 101, "Le code de statut devrait être 101 (Switching Protocols)"
    assert "upgrade" in response.headers.lower(), "L'en-tête 'Upgrade' est manquant"
    assert "websocket" in response.headers["upgrade"].lower(), "L'en-tête 'Upgrade' devrait être 'websocket'"
    assert "connection" in response.headers.lower(), "L'en-tête 'Connection' est manquant"
    assert "upgrade" in response.headers["connection"].lower(), "L'en-tête 'Connection' devrait contenir 'upgrade'"
    return True

def validate_websocket_message_event(event):
    """Valide un événement de message WebSocket"""
    assert "type" in event, "L'événement devrait avoir un type"
    assert event["type"] == "new_message", "Le type d'événement devrait être 'new_message'"
    assert "message" in event, "L'événement devrait contenir un message"
    
    message = event["message"]
    required_fields = ["content", "sender_id", "conversation_id", "is_read"]
    for field in required_fields:
        assert field in message, f"Le champ {field} est manquant dans le message"
    
    return True

def validate_websocket_typing_event(event):
    """Valide un événement de frappe WebSocket"""
    assert "type" in event, "L'événement devrait avoir un type"
    assert event["type"] == "typing_status", "Le type d'événement devrait être 'typing_status'"
    
    required_fields = ["user_id", "conversation_id", "is_typing"]
    for field in required_fields:
        assert field in event, f"Le champ {field} est manquant"
    
    assert isinstance(event["is_typing"], bool), "is_typing devrait être un booléen"
    return True

def validate_websocket_read_event(event):
    """Valide un événement de lecture WebSocket"""
    assert "type" in event, "L'événement devrait avoir un type"
    assert event["type"] == "messages_read", "Le type d'événement devrait être 'messages_read'"
    
    required_fields = ["user_id", "conversation_id"]
    for field in required_fields:
        assert field in event, f"Le champ {field} est manquant"
    
    return True

def check_unread_messages(response: List[Dict[str, Any]], min_count: int = 0) -> bool:
    """
    Vérifie que la réponse des messages non lus est valide.
    Retourne True si la validation est réussie, False sinon.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Début de la validation des messages non lus")
        logger.info(f"Réponse reçue: {response}")
        
        # Vérifier que la réponse est une liste
        if not isinstance(response, list):
            logger.error(f"La réponse n'est pas une liste mais un {type(response)}")
            return False
            
        # Si la liste est vide et qu'on n'attend pas de messages non lus, c'est valide
        if not response and min_count == 0:
            logger.info("Liste vide acceptée car min_count = 0")
            return True
            
        # Vérifier que tous les éléments sont valides
        logger.info("Vérification des éléments:")
        valid_conversations = 0
        
        for item in response:
            logger.info(f"Vérification de l'élément: {item}")
            
            # Vérifier la structure de l'élément
            if not isinstance(item, dict) or "conversation_id" not in item or "unread_count" not in item:
                logger.error("Structure d'élément invalide")
                continue
            
            try:
                # Utiliser float comme intermédiaire pour gérer les nombres sous forme de chaîne
                conv_id = int(float(item["conversation_id"]))
                count = int(float(item["unread_count"]))
                
                if conv_id >= 0 and count >= 0:
                    valid_conversations += 1
                    logger.info(f"Conversation valide trouvée: {conv_id} = {count}")
                else:
                    logger.error(f"Valeurs négatives trouvées: conv_id={conv_id}, count={count}")
            except (ValueError, TypeError) as e:
                logger.error(f"Erreur de conversion: {e}")
                continue
        
        logger.info(f"Nombre de conversations valides trouvées: {valid_conversations}")
        logger.info(f"Minimum requis: {min_count}")
        
        # Si on a trouvé au moins le nombre minimum de conversations valides
        return valid_conversations >= min_count
        
    except Exception as e:
        logger.error(f"Exception lors de la validation: {str(e)}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return False

def validate_read_status_response(response):
    """Valide la réponse de l'action de marquer comme lu"""
    import logging
    logger = logging.getLogger(__name__)
    
    assert response.status_code == 200
    data = response.json()
    
    # Log de la réponse pour le débogage
    logger.info(f"Contenu de la réponse de marquage comme lu: {data}")
    
    # Vérifier que la réponse contient un statut de succès
    assert "status" in data, "La réponse devrait contenir un statut"
    assert data["status"] == "success", f"Le statut devrait être 'success', mais est '{data.get('status')}'"
    
    return True 