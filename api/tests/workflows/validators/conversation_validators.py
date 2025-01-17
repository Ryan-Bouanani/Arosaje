def validate_conversation_response(response, expected_participants_count=None, expected_messages_count=None, conversation_type=None):
    """Valide la réponse d'une conversation"""
    assert response.status_code == 200
    data = response.json()
    
    # Vérification des champs obligatoires
    required_fields = ["id", "created_at", "updated_at", "participants", "messages", "type"]
    for field in required_fields:
        assert field in data, f"Le champ {field} est manquant dans la réponse"
    
    # Vérifier le nombre de participants
    if expected_participants_count is not None:
        assert len(data["participants"]) == expected_participants_count, \
            f"Nombre de participants incorrect. Attendu: {expected_participants_count}, Reçu: {len(data['participants'])}"
    
    # Vérifier le nombre de messages
    if expected_messages_count is not None:
        assert len(data["messages"]) == expected_messages_count, \
            f"Nombre de messages incorrect. Attendu: {expected_messages_count}, Reçu: {len(data['messages'])}"
    
    # Vérifier le type de conversation
    if conversation_type is not None:
        assert data["type"] == conversation_type, \
            f"Type de conversation incorrect. Attendu: {conversation_type}, Reçu: {data['type']}"
    
    return True 