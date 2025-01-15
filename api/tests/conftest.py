import pytest
import os
import shutil
import sys
from pathlib import Path

# Ajouter le dossier parent (api) au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PIL import Image
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from utils.database import Base, get_db

# Import des modèles pour s'assurer qu'ils sont enregistrés avec Base
from models.user import User
from models.plant import Plant
from models.photo import Photo
from models.garde import Garde
from models.advice import Advice

from reset_test_db import reset_test_database, check_tables

# Chemins des bases de données avec chemins absolus
TEST_DB_DIR = ROOT_DIR / "tests" / "assets" / "database"
TEST_DB_PATH = TEST_DB_DIR / "arosaje_test.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

def get_test_db():
    """Fonction pour obtenir une session de base de données de test"""
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Configure la base de données de test"""
    # Initialiser/réinitialiser la base de test
    reset_test_database()
    
    # Vérifier que les tables ont été créées
    engine = create_engine(TEST_DATABASE_URL)
    tables = check_tables(engine)
    print(f"Tables disponibles pour les tests: {tables}")
    
    # Remplacer la fonction get_db par get_test_db dans les dépendances
    import routers.auth
    import routers.plant
    import routers.photo
    routers.auth.get_db = get_test_db
    routers.plant.get_db = get_test_db
    routers.photo.get_db = get_test_db
    
    yield

@pytest.fixture
def api_url():
    """URL de base de l'API pour les tests"""
    return "http://localhost:8000"

@pytest.fixture
def test_user_email():
    """Email de test"""
    return f"test_{os.urandom(4).hex()}@example.com"  # Email unique à chaque test

@pytest.fixture
def test_password():
    """Mot de passe de test"""
    return "test123secure"

@pytest.fixture
def test_image_path():
    """Chemin vers une image de test"""
    # Créer le dossier de test s'il n'existe pas
    test_assets = ROOT_DIR / "tests" / "assets"
    test_assets.mkdir(parents=True, exist_ok=True)
    
    # Créer une image de test si elle n'existe pas
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
    
    # Créer un fichier texte invalide
    invalid_file = test_assets / "invalid_file.txt"
    if not invalid_file.exists():
        with open(invalid_file, "w") as f:
            f.write("Ceci n'est pas une image")
    
    return str(invalid_file) 