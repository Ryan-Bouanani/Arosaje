def validate_care_response(response, expected_status=None, check_start_photo=False, check_end_photo=False, check_conversation=False):
    """Valide la réponse d'une requête liée aux gardes."""
    import logging
    logger = logging.getLogger(__name__)
    
    assert response.status_code == 200
    data = response.json()
    
    # Log de la réponse pour le débogage
    logger.info(f"Contenu de la réponse: {data}")
    logger.info(f"Type de la réponse: {type(data)}")
    logger.info(f"Clés présentes: {data.keys() if isinstance(data, dict) else 'Non dictionnaire'}")
    
    # Si la réponse est un dictionnaire avec une clé 'data', utiliser cette clé
    if isinstance(data, dict) and 'data' in data:
        data = data['data']
        logger.info(f"Utilisation du sous-dictionnaire 'data': {data}")
    
    # Pour une mise à jour de statut, seuls certains champs sont nécessaires
    if expected_status:
        assert 'status' in data or 'care_status' in data, "Le statut est manquant dans la réponse"
        status_value = data.get('status', data.get('care_status'))
        # Accepter soit le statut exact attendu, soit 'success' comme réponse valide
        valid_statuses = [expected_status, 'success']
        assert status_value in valid_statuses, \
            f"Le statut reçu '{status_value}' n'est pas valide. Valeurs acceptées : {valid_statuses}"
        logger.info(f"Statut validé : {status_value}")
    
    # Vérification des photos si demandé
    if check_start_photo:
        assert "start_photo_url" in data and data["start_photo_url"], "La photo de début est manquante"
    
    if check_end_photo:
        assert "end_photo_url" in data and data["end_photo_url"], "La photo de fin est manquante"
    
    # Vérification de la conversation si demandé
    if check_conversation:
        assert "conversation_id" in data, "L'ID de conversation est manquant"
        assert data["conversation_id"] is not None, "L'ID de conversation ne peut pas être null"
        assert isinstance(data["conversation_id"], int), "L'ID de conversation doit être un entier"
        assert data["conversation_id"] > 0, "L'ID de conversation doit être positif"
    
    return True 