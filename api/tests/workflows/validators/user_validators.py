from typing import Dict, Any

def validate_user_response(response: Dict[str, Any]) -> None:
    """Valide la réponse de création/mise à jour d'un utilisateur"""
    assert isinstance(response["id"], int), "L'ID doit être un entier"
    assert isinstance(response["email"], str), "L'email doit être une chaîne"
    assert isinstance(response["nom"], str), "Le nom doit être une chaîne"
    assert isinstance(response["prenom"], str), "Le prénom doit être une chaîne"
    assert isinstance(response["role"], str), "Le rôle doit être une chaîne"
    if "telephone" in response:
        assert isinstance(response["telephone"], str), "Le téléphone doit être une chaîne"
    if "localisation" in response:
        assert isinstance(response["localisation"], str), "La localisation doit être une chaîne" 