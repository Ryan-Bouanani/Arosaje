import os
from pathlib import Path
from fastapi import UploadFile
from PIL import Image
import uuid
from typing import Tuple

# Configuration
IMG_DIR = Path("assets/img")
PERSISTED_IMG_DIR = Path("assets/persisted_img")
TEMP_IMG_DIR = Path("assets/temp_img")
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
        
        # Choisir le dossier approprié
        if "temp" in type.lower():
            target_dir = TEMP_IMG_DIR
        elif "persisted" in type.lower():
            target_dir = PERSISTED_IMG_DIR
        else:
            target_dir = IMG_DIR
            
        filepath = target_dir / filename

        # Créer le dossier si nécessaire
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Lire et sauvegarder le fichier
            content = await file.read()
            with open(str(filepath), "wb") as f:
                f.write(content)

            # Optimiser l'image avec PIL
            try:
                with Image.open(filepath) as img:
                    # Convertir en RGB si nécessaire
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    # Redimensionner si trop grande
                    if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                        img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                        img.save(str(filepath), quality=85, optimize=True)
            except Exception:
                pass

            # Générer l'URL
            url = f"{target_dir.parts[-2]}/{target_dir.parts[-1]}/{filename}"
            final_url = url.replace("\\", "/")
            return filename, final_url

        except Exception as e:
            # En cas d'erreur, supprimer le fichier s'il existe
            if filepath.exists():
                filepath.unlink()
            raise Exception(f"Erreur lors de la sauvegarde de l'image : {e}")

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