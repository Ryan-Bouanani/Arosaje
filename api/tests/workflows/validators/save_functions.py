def save_int(response, value):
    """Convertit et sauvegarde une valeur en entier"""
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Impossible de convertir '{value}' en entier")

def prepare_participant_ids(response, owner_id, botanist_id):
    """Prépare les IDs des participants pour la création de conversation"""
    try:
        # Convertir les IDs en entiers
        owner_id = int(owner_id)
        botanist_id = int(botanist_id)
        
        # Retourner la liste des IDs
        return [owner_id, botanist_id]
    except (ValueError, TypeError) as e:
        raise AssertionError(f"Erreur lors de la préparation des IDs: {str(e)}") 