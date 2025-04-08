import pytest
import os
import sys
from pathlib import Path

# Ajouter le dossier parent (api) au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Ajouter le dossier des tests au PYTHONPATH
TEST_DIR = Path(__file__).parent
sys.path.insert(0, str(TEST_DIR))

# Ajouter le dossier workflows au PYTHONPATH
WORKFLOWS_DIR = TEST_DIR / "workflows"
sys.path.insert(0, str(WORKFLOWS_DIR))

from PIL import Image

# Fixtures pour les tests
@pytest.fixture
def api_url():
    """URL de base de l'API pour les tests"""
    return "http://localhost:8000"

@pytest.fixture
def ws_url():
    """URL de base WebSocket pour les tests"""
    return "ws://localhost:8000"

@pytest.fixture
def test_user_email():
    """Email de test"""
    import uuid
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

@pytest.fixture
def test_password():
    """Mot de passe de test"""
    return "test123secure"

@pytest.fixture
def admin_email():
    """Email admin pour les tests"""
    return "root@arosaje.fr"

@pytest.fixture
def admin_password():
    """Mot de passe admin pour les tests"""
    return "epsi691"

@pytest.fixture
def test_image_path():
    """Chemin vers une image de test"""
    return str(TEST_DIR / "assets" / "test_plant.jpg")

@pytest.fixture
def invalid_file_path():
    """Chemin vers un fichier texte invalide pour les tests"""
    return str(TEST_DIR / "assets" / "invalid_file.txt") 