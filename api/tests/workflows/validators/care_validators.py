def validate_care_response(response, expected_status=None, check_start_photo=False, check_end_photo=False, check_conversation=False):
    """Valide la réponse d'une requête liée aux gardes."""
    assert response.status_code == 200
    data = response.json()
    
    # Vérification des champs obligatoires
    required_fields = ["id", "plant_id", "owner_id", "caretaker_id", "start_date", "end_date", "status", "created_at", "updated_at"]
    for field in required_fields:
        assert field in data, f"Le champ {field} est manquant dans la réponse"
    
    # Vérification du statut si spécifié
    if expected_status:
        assert data["status"] == expected_status, f"Le statut attendu était {expected_status}, mais a reçu {data['status']}"
    
    # Vérification des photos si demandé
    if check_start_photo:
        assert "start_photo_url" in data and data["start_photo_url"], "La photo de début est manquante"
    
    if check_end_photo:
        assert "end_photo_url" in data and data["end_photo_url"], "La photo de fin est manquante"
    
    # Vérification de la conversation si demandé
    if check_conversation:
        assert "conversation_id" in data and data["conversation_id"], "L'ID de conversation est manquant"
        assert isinstance(data["conversation_id"], int), "L'ID de conversation doit être un entier"
    
    return True 