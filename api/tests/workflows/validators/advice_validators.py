def validate_advice_response(response, expected_status=None):
    """Valide la réponse d'une requête liée aux conseils du système unifié."""
    assert response.status_code == 200
    data = response.json()
    
    # Vérification des champs obligatoires du nouveau système
    required_fields = [
        "id", "title", "content", "plant_care_id", "botanist_id", 
        "priority", "validation_status", "version", "is_current_version",
        "created_at", "updated_at"
    ]
    for field in required_fields:
        assert field in data, f"Le champ {field} est manquant dans la réponse"
    
    # Vérification du statut de validation si spécifié
    if expected_status:
        assert data["validation_status"] == expected_status, f"Le statut attendu était {expected_status}, mais a reçu {data['validation_status']}"
    
    # Vérification des valeurs par défaut
    assert data["version"] >= 1, "La version doit être >= 1"
    assert isinstance(data["is_current_version"], bool), "is_current_version doit être un boolean"
    assert data["priority"] in ["normal", "urgent", "follow_up"], "Priority doit être valide"
    assert data["validation_status"] in ["pending", "validated", "rejected", "needs_revision"], "Validation status doit être valide"
    
    return True 