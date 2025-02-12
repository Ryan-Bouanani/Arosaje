def save_int(response, value):
    """Convertit et sauvegarde une valeur en entier"""
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Impossible de convertir '{value}' en entier") 