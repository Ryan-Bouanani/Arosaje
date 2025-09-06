import os
import re
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image
import uuid
from typing import Tuple

# Configuration
IMG_DIR = Path("assets/img")
PERSISTED_IMG_DIR = Path("assets/persisted_img")
ORIGINAL_IMG_DIR = Path("assets/original_img")
PREVIEW_IMG_DIR = Path("assets/preview_img")
TEMP_IMG_DIR = Path("assets/temp_img")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_IMAGE_SIZE = (2048, 2048)  # Haute qualité pour tous formats
PREVIEW_SIZE = (1200, 1200)  # Aperçu optimisé
THUMBNAIL_SIZE = (300, 300)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB en bytes

# Magic bytes pour validation MIME
ALLOWED_SIGNATURES = {
    b"\xff\xd8\xff": [".jpg", ".jpeg"],  # JPEG
    b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": [".png"],  # PNG
    b"\x47\x49\x46\x38": [".gif"],  # GIF
}


class ImageHandler:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sécurise le nom de fichier contre path traversal et caractères dangereux"""
        if not filename:
            raise HTTPException(status_code=400, detail="Nom de fichier manquant")

        # Supprimer path traversal et caractères dangereux
        filename = os.path.basename(filename)  # Supprime les chemins
        filename = re.sub(
            r'[<>:"/\\|?*]', "", filename
        )  # Supprime caractères dangereux
        filename = filename.strip(". ")  # Supprime points/espaces en début/fin

        if not filename or len(filename) > 100:
            raise HTTPException(status_code=400, detail="Nom de fichier invalide")

        return filename

    @staticmethod
    def validate_file_signature(content: bytes, filename: str) -> bool:
        """Valide la signature binaire du fichier (magic bytes)"""
        extension = Path(filename).suffix.lower()

        # Vérifier les magic bytes
        for signature, allowed_exts in ALLOWED_SIGNATURES.items():
            if content.startswith(signature) and extension in allowed_exts:
                return True

        return False

    @staticmethod
    def is_valid_image(file: UploadFile) -> bool:
        """Vérifie si le fichier est une image valide avec validation complète"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier manquant")

        # Sécuriser le nom de fichier
        safe_filename = ImageHandler.sanitize_filename(file.filename)

        # Vérifier l'extension
        extension = Path(safe_filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporté. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        return True

    @staticmethod
    async def save_image(file: UploadFile, type: str) -> Tuple[str, str]:
        """Sauvegarde et optimise l'image avec validation de sécurité complète"""
        # Validation préalable
        ImageHandler.is_valid_image(file)

        # Lire le contenu avec limite de taille
        content = b""
        total_size = 0

        while chunk := await file.read(8192):  # Lecture par chunks de 8KB
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"Fichier trop volumineux. Taille maximum: {MAX_FILE_SIZE // (1024*1024)}MB",
                )
            content += chunk

        # Validation de la signature binaire
        safe_filename = ImageHandler.sanitize_filename(file.filename)
        if not ImageHandler.validate_file_signature(content, safe_filename):
            raise HTTPException(
                status_code=400,
                detail="Le contenu du fichier ne correspond pas à son extension",
            )

        # Créer un nom de fichier unique sécurisé
        ext = Path(safe_filename).suffix.lower()
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
            # Sauvegarder le fichier (contenu déjà en mémoire, sécurisé)
            with open(str(filepath), "wb") as f:
                f.write(content)

            # Optimiser l'image avec PIL
            try:
                with Image.open(filepath) as img:
                    file_extension = safe_filename.suffix.lower()

                    # Traitement selon le format
                    if file_extension == ".png":
                        # Pour PNG : conserver l'alpha, convertir palette vers RGBA
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        # RGBA reste RGBA, RGB reste RGB
                    else:
                        # Pour JPEG/autres : convertir en RGB si nécessaire
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")

                    # Redimensionner si trop grande avec algorithme optimisé
                    needs_resize = (
                        img.size[0] > MAX_IMAGE_SIZE[0]
                        or img.size[1] > MAX_IMAGE_SIZE[1]
                    )

                    if needs_resize:
                        # BICUBIC préserve mieux la netteté que LANCZOS
                        img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.BICUBIC)

                    # Sauvegarder avec les bons paramètres selon le format (toujours optimiser)
                    if file_extension == ".png":
                        # PNG: compression moins agressive pour préserver la qualité
                        img.save(str(filepath), optimize=True, compress_level=3)
                    else:
                        # JPEG et autres formats: qualité plus élevée
                        img.save(str(filepath), quality=90, optimize=True)
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
    async def save_image_dual(file: UploadFile, type: str) -> Tuple[str, str, str, str]:
        """Sauvegarde original + preview avec validation de sécurité complète
        Retourne: (preview_filename, preview_url, original_filename, original_url)"""

        # Validation préalable
        ImageHandler.is_valid_image(file)

        # Lire le contenu avec limite de taille
        content = b""
        total_size = 0

        while chunk := await file.read(8192):
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"Fichier trop volumineux. Taille maximum: {MAX_FILE_SIZE // (1024*1024)}MB",
                )
            content += chunk

        # Validation de la signature binaire
        safe_filename = ImageHandler.sanitize_filename(file.filename)
        if not ImageHandler.validate_file_signature(content, safe_filename):
            raise HTTPException(
                status_code=400,
                detail="Le contenu du fichier ne correspond pas à son extension",
            )

        # Créer des noms de fichiers uniques
        ext = Path(safe_filename).suffix.lower()
        base_uuid = str(uuid.uuid4())
        original_filename = f"{type}_original_{base_uuid}{ext}"
        preview_filename = f"{type}_preview_{base_uuid}{ext}"

        # Chemins des fichiers
        original_filepath = ORIGINAL_IMG_DIR / original_filename
        preview_filepath = PREVIEW_IMG_DIR / preview_filename

        # Créer les dossiers si nécessaire
        ORIGINAL_IMG_DIR.mkdir(parents=True, exist_ok=True)
        PREVIEW_IMG_DIR.mkdir(parents=True, exist_ok=True)

        try:
            # Sauvegarder l'original intact
            with open(str(original_filepath), "wb") as f:
                f.write(content)

            # Créer le preview optimisé
            with Image.open(original_filepath) as img:
                file_extension = Path(safe_filename).suffix.lower()

                # Traitement selon le format pour preview
                if file_extension == ".png":
                    # Pour PNG : conserver l'alpha
                    if img.mode == "P":
                        img = img.convert("RGBA")
                else:
                    # Pour JPEG/autres : convertir en RGB si nécessaire
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                # Créer le preview (redimensionné)
                preview_img = img.copy()
                if (
                    preview_img.size[0] > PREVIEW_SIZE[0]
                    or preview_img.size[1] > PREVIEW_SIZE[1]
                ):
                    preview_img.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)

                # Sauvegarder le preview avec les bons paramètres
                if file_extension == ".png":
                    preview_img.save(
                        str(preview_filepath), optimize=True, compress_level=6
                    )
                else:
                    preview_img.save(str(preview_filepath), quality=90, optimize=True)

            # Générer les URLs
            original_url = f"original_img/{original_filename}".replace("\\", "/")
            preview_url = f"preview_img/{preview_filename}".replace("\\", "/")

            return preview_filename, preview_url, original_filename, original_url

        except Exception as e:
            # En cas d'erreur, supprimer les fichiers s'ils existent
            if original_filepath.exists():
                original_filepath.unlink()
            if preview_filepath.exists():
                preview_filepath.unlink()
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
