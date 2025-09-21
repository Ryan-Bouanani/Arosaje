"""
Utilitaires pour la gestion et optimisation des images
"""
import base64
import io
from typing import Optional
from PIL import Image


def generate_thumbnail(base64_image: str, size: tuple = (150, 150)) -> Optional[str]:
    """
    Génère un thumbnail à partir d'une image base64

    Args:
        base64_image: Image encodée en base64
        size: Taille du thumbnail (largeur, hauteur)

    Returns:
        Thumbnail encodé en base64 ou None si erreur
    """
    try:
        # Décoder l'image base64
        if base64_image.startswith('data:image'):
            # Supprimer le préfixe data:image/xxx;base64,
            base64_data = base64_image.split(',')[1]
        else:
            base64_data = base64_image

        image_data = base64.b64decode(base64_data)

        # Ouvrir l'image avec PIL
        image = Image.open(io.BytesIO(image_data))

        # Convertir en RGB si nécessaire (pour PNG avec transparence)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Créer un fond blanc pour remplacer la transparence
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        # Redimensionner avec ratio préservé (fit dans le carré)
        image.thumbnail(size, Image.Resampling.LANCZOS)

        # Créer une image carrée avec fond blanc
        thumbnail = Image.new('RGB', size, (255, 255, 255))

        # Centrer l'image redimensionnée
        x = (size[0] - image.width) // 2
        y = (size[1] - image.height) // 2
        thumbnail.paste(image, (x, y))

        # Encoder en base64
        buffer = io.BytesIO()
        thumbnail.save(buffer, format='JPEG', quality=85, optimize=True)
        thumbnail_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return f"data:image/jpeg;base64,{thumbnail_base64}"

    except Exception as e:
        print(f"Erreur génération thumbnail: {e}")
        return None


def calculate_image_size(base64_image: str) -> dict:
    """
    Calcule la taille d'une image base64

    Returns:
        Dict avec width, height, size_kb
    """
    try:
        if base64_image.startswith('data:image'):
            base64_data = base64_image.split(',')[1]
        else:
            base64_data = base64_image

        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data))

        return {
            'width': image.width,
            'height': image.height,
            'size_kb': len(base64_data) / 1024
        }
    except Exception:
        return {'width': 0, 'height': 0, 'size_kb': 0}