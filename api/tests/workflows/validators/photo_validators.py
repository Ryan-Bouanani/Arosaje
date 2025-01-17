from typing import Any, Dict, List

def verify_photo_list(response: Any, expected_count: int = None) -> None:
    """Vérifie que la réponse contient une liste de photos valide"""
    
    # Extraire le JSON de la réponse
    try:
        json_response = response.json() if hasattr(response, 'json') else response
    except AttributeError:
        json_response = response
    
    # Si la réponse est un dictionnaire avec une clé 'photos', extraire la liste
    if isinstance(json_response, dict) and 'photos' in json_response:
        photos = json_response['photos']
    else:
        photos = json_response
        
    assert isinstance(photos, list), "La réponse doit être une liste de photos"
    
    # Vérifier le nombre de photos si spécifié
    if expected_count is not None:
        assert len(photos) == expected_count, f"Le nombre de photos attendu est {expected_count}, reçu {len(photos)}"
    
    # Vérifier chaque photo dans la liste
    for photo in photos:
        assert isinstance(photo, dict), "Chaque photo doit être un dictionnaire"
        assert 'id' in photo, "Chaque photo doit avoir un id"
        assert 'filename' in photo, "Chaque photo doit avoir un filename"
        assert 'url' in photo, "Chaque photo doit avoir une url"
        assert 'plant_id' in photo, "Chaque photo doit avoir un plant_id"
        assert 'type' in photo, "Chaque photo doit avoir un type"
        assert 'description' in photo, "Chaque photo doit avoir une description"
        assert 'created_at' in photo, "Chaque photo doit avoir une date de création"

def validate_photo_response(response: Any) -> None:
    """Valide la réponse d'un upload de photo"""
    try:
        json_response = response.json() if hasattr(response, 'json') else response
    except AttributeError:
        json_response = response
        
    assert isinstance(json_response, dict), "La réponse doit être un dictionnaire"
    assert 'id' in json_response, "La réponse doit contenir un id"
    assert 'url' in json_response, "La réponse doit contenir une url"
    assert 'filename' in json_response, "La réponse doit contenir un filename"
    assert 'created_at' in json_response, "La réponse doit contenir une date de création" 