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