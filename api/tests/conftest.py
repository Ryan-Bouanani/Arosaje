import pytest
import os
import sys
from pathlib import Path

# Ajouter le dossier parent (api) au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PIL import Image

@pytest.fixture
def api_url():
    """URL de base de l'API pour les tests"""
    return "http://localhost:8000"

@pytest.fixture
def test_user_email():
    """Email de test"""
    return f"test_{os.urandom(4).hex()}@example.com"

@pytest.fixture
def test_password():
    """Mot de passe de test"""
    return "test123secure"

@pytest.fixture
def test_image_path():
    """Chemin vers une image de test"""
    test_assets = ROOT_DIR / "tests" / "assets"
    test_assets.mkdir(parents=True, exist_ok=True)
    
    test_image = test_assets / "test_plant.jpg"
    if not test_image.exists():
        img = Image.new('RGB', (100, 100), color='green')
        img.save(test_image)
    
    return str(test_image)

@pytest.fixture
def invalid_file_path():
    """Chemin vers un fichier texte invalide pour les tests"""
    test_assets = ROOT_DIR / "tests" / "assets"
    test_assets.mkdir(parents=True, exist_ok=True)
    
    invalid_file = test_assets / "invalid_file.txt"
    if not invalid_file.exists():
        with open(invalid_file, "w") as f:
            f.write("Ceci n'est pas une image")
    
    return str(invalid_file) 