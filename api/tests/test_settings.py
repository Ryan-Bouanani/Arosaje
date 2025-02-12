from pathlib import Path

# Chemin de base des tests
TEST_DIR = Path(__file__).resolve().parent
ROOT_DIR = TEST_DIR.parent

# Configuration pour les tests
DEBUG_MODE = True
PROJECT_NAME = "A'rosa-je API Test"
VERSION = "1.0.0-test"

# Configuration des chemins de test
TEST_ASSETS_DIR = TEST_DIR / "assets"
TEST_ASSETS_DIR.mkdir(parents=True, exist_ok=True) 