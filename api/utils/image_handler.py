import os
from pathlib import Path
from fastapi import UploadFile
from PIL import Image
import uuid
from typing import Tuple

# Configuration
IMG_DIR = Path("assets/img")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_IMAGE_SIZE = (1920, 1080)  # Full HD
THUMBNAIL_SIZE = (300, 300)

class ImageHandler:
    @staticmethod
    def is_valid_image(file: UploadFile) -> bool:
        """Vérifie si le fichier est une image valide"""
        return Path(file.filename).suffix.lower() in ALLOWED_EXTENSIONS

    @staticmethod
    async def save_image(file: UploadFile, type: str) -> Tuple[str, str]:
        """Sauvegarde et optimise l'image"""
        # Créer un nom de fichier unique
        ext = Path(file.filename).suffix.lower()
        filename = f"{type}_{uuid.uuid4()}{ext}"
        filepath = IMG_DIR / filename

        # Créer le dossier si nécessaire
        IMG_DIR.mkdir(parents=True, exist_ok=True)

        # Sauvegarder le fichier original
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)

        # Optimiser l'image
        with Image.open(filepath) as img:
            # Convertir en RGB si nécessaire
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionner si trop grande
            if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                img.save(filepath, quality=85, optimize=True)

        # Générer l'URL (s'assurer qu'elle commence par un slash)
        url = f"/assets/img/{filename}"
        if not url.startswith("/"):
            url = f"/{url}"
        
        return filename, url

    @staticmethod
    def delete_image(filename: str) -> bool:
        """Supprime une image"""
        try:
            filepath = IMG_DIR / filename
            if filepath.exists():
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False 