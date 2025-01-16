def validate_photo_response(response):
    """Valide la réponse de l'upload de photo"""
    # Accéder au contenu JSON de la réponse
    json_response = response.json()
    
    assert "id" in json_response
    assert "url" in json_response
    assert json_response["url"].startswith("/assets/img/")
    assert "filename" in json_response
    assert "created_at" in json_response
    return True

def validate_care_response(response, expected_status=None, check_start_photo=False, check_end_photo=False):
    """Valide la réponse de l'API de garde"""
    json_response = response.json()
    
    # Vérifier les champs obligatoires
    required_fields = [
        "id", "plant_id", "owner_id", "caretaker_id",
        "start_date", "end_date", "status",
        "created_at", "updated_at"
    ]
    for field in required_fields:
        assert field in json_response, f"Champ manquant: {field}"
    
    # Vérifier le statut si spécifié
    if expected_status:
        assert json_response["status"] == expected_status, \
            f"Statut incorrect. Attendu: {expected_status}, Reçu: {json_response['status']}"
    
    # Vérifier les photos si demandé
    if check_start_photo:
        assert "start_photo_url" in json_response
        assert json_response["start_photo_url"] is not None
        assert json_response["start_photo_url"].startswith("/assets/img/")
    
    if check_end_photo:
        assert "end_photo_url" in json_response
        assert json_response["end_photo_url"] is not None
        assert json_response["end_photo_url"].startswith("/assets/img/")
    
    # Vérifier la cohérence des dates
    assert json_response["end_date"] > json_response["start_date"], \
        "La date de fin doit être postérieure à la date de début"
    
    return True 

def validate_advice_response(response, expected_status=None):
    """Valide la réponse d'une requête liée aux conseils."""
    assert response.status_code == 200
    data = response.json()
    
    # Vérification des champs obligatoires
    required_fields = ["id", "texte", "status", "botanist_id", "plant_id", "created_at", "updated_at"]
    for field in required_fields:
        assert field in data, f"Le champ {field} est manquant dans la réponse"
    
    # Vérification du statut si spécifié
    if expected_status:
        assert data["status"] == expected_status, f"Le statut attendu était {expected_status}, mais a reçu {data['status']}"
    
    return True 