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