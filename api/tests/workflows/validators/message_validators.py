def validate_message_response(response, expected_sender_id=None, max_length=2000):
    """Valide la réponse d'un message"""
    assert response.status_code == 200
    data = response.json()
    
    # Vérification des champs obligatoires
    required_fields = ["id", "content", "sender_id", "conversation_id", "created_at", "updated_at", "is_read"]
    for field in required_fields:
        assert field in data, f"Le champ {field} est manquant dans la réponse"
    
    # Vérifier l'expéditeur si spécifié
    if expected_sender_id is not None:
        assert data["sender_id"] == expected_sender_id, \
            f"ID de l'expéditeur incorrect. Attendu: {expected_sender_id}, Reçu: {data['sender_id']}"
    
    # Vérifier la longueur du message
    assert len(data["content"]) <= max_length, \
        f"Le message dépasse la longueur maximale autorisée de {max_length} caractères"
    
    return True

def validate_messages_list_response(response, expected_page=None, expected_per_page=None, expected_count=None, expected_content=None):
    """Valide la réponse d'une liste de messages"""
    assert response.status_code == 200
    data = response.json()
    
    # Gérer les deux formats possibles de réponse
    messages = data if isinstance(data, list) else data.get("messages", [])
    
    # Vérifier le nombre de messages si spécifié
    if expected_count is not None:
        assert len(messages) == expected_count, \
            f"Nombre de messages incorrect. Attendu: {expected_count}, Reçu: {len(messages)}"
    
    # Vérifier le contenu si spécifié
    if expected_content is not None:
        found = False
        for message in messages:
            if expected_content in message["content"]:
                found = True
                break
        assert found, f"Message avec le contenu '{expected_content}' non trouvé"
    
    # Vérifier la pagination si présente
    if not isinstance(data, list) and "pagination" in data:
        pagination = data["pagination"]
        if expected_page is not None:
            assert pagination["page"] == expected_page, \
                f"Page incorrecte. Attendu: {expected_page}, Reçu: {pagination['page']}"
        
        if expected_per_page is not None:
            assert pagination["per_page"] == expected_per_page, \
                f"Nombre d'éléments par page incorrect. Attendu: {expected_per_page}, Reçu: {pagination['per_page']}"
    
    # Vérifier chaque message
    for message in messages:
        required_fields = ["id", "content", "sender_id", "conversation_id", "created_at", "updated_at", "is_read"]
        for field in required_fields:
            assert field in message, f"Le champ {field} est manquant dans un message"
    
    return True

def validate_unread_count_response(response):
    """Valide la réponse du compteur de messages non lus"""
    assert response.status_code == 200
    data = response.json()
    
    assert "unread_count" in data, "La réponse devrait contenir une clé 'unread_count'"
    assert isinstance(data["unread_count"], int), "Le compteur de messages non lus devrait être un entier"
    assert data["unread_count"] >= 0, "Le compteur de messages non lus ne peut pas être négatif"
    
    return True 