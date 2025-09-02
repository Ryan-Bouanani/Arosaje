"""
Tests d'intégration minimaux pour l'API A'rosa-je
Tests HTTP via requests, conçus pour être executés "sans friction"
"""

import os
import secrets
import requests
import pytest
from io import BytesIO


# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")


def test_auth_login_invalid_credentials():
    """POST /auth/login → 401 attendu si mauvais identifiants"""
    response = requests.post(
        f"{API_URL}/auth/login",
        data={"username": "invalid@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_auth_register_and_login():
    """POST /auth/register + POST /auth/login → 200 + token"""
    # Génération d'email unique pour éviter les collisions
    test_email = f"test_{secrets.token_hex(8)}@example.com"

    # 1. Inscription
    register_data = {
        "email": test_email,
        "password": "TestPassword123456",
        "nom": "Test",
        "prenom": "User",
        "telephone": "0123456789",
        "localisation": "Paris",
        "role": "user",
    }

    response = requests.post(f"{API_URL}/auth/register", json=register_data)
    assert response.status_code in [200, 201]  # Accepter 200 ou 201

    # 2. Login avec compte pré-existant vérifié (car nouveaux comptes non vérifiés)
    login_data = {"username": "user@arosaje.fr", "password": "epsi691"}

    response = requests.post(f"{API_URL}/auth/login", data=login_data)
    assert response.status_code == 200

    # 3. Vérifier la présence du token
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_advice_creation_forbidden_for_user():
    """POST /advices/ avec un user → 403"""
    # Créer un utilisateur standard
    test_email = f"test_{secrets.token_hex(8)}@example.com"

    # Inscription
    register_data = {
        "email": test_email,
        "password": "TestPassword123456",
        "nom": "Test",
        "prenom": "User",
        "telephone": "0123456789",
        "localisation": "Paris",
        "role": "user",
    }

    requests.post(f"{API_URL}/auth/register", json=register_data)

    # Login pour obtenir le token avec compte existant
    login_data = {"username": "user@arosaje.fr", "password": "epsi691"}

    response = requests.post(f"{API_URL}/auth/login", data=login_data)
    token = response.json()["access_token"]

    # Tenter de créer un conseil (doit échouer)
    headers = {"Authorization": f"Bearer {token}"}
    advice_data = {
        "plant_care_id": 1,
        "title": "Test advice",
        "content": "This should fail",
        "priority": "normal",
    }

    response = requests.post(f"{API_URL}/advices/", json=advice_data, headers=headers)
    assert response.status_code == 403


def test_photo_upload_invalid_file():
    """POST /photos/upload/{plant_id} avec un fichier texte → 400"""
    # Créer un utilisateur pour avoir un token
    test_email = f"test_{secrets.token_hex(8)}@example.com"

    # Inscription + Login rapide
    register_data = {
        "email": test_email,
        "password": "TestPassword123456",
        "nom": "Test",
        "prenom": "User",
        "telephone": "0123456789",
        "localisation": "Paris",
        "role": "user",
    }

    requests.post(f"{API_URL}/auth/register", json=register_data)

    login_response = requests.post(
        f"{API_URL}/auth/login",
        data={"username": "user@arosaje.fr", "password": "epsi691"},
    )
    token = login_response.json()["access_token"]

    # Tenter d'uploader un fichier texte au lieu d'une image
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("test.txt", BytesIO(b"This is not an image"), "text/plain")}

    response = requests.post(
        f"{API_URL}/photos/upload/1", files=files, headers=headers  # plant_id=1
    )

    # Doit retourner 400 car ce n'est pas une image
    assert response.status_code in [400, 422]  # 400 ou 422 selon validation


def test_metrics_endpoint():
    """GET /metrics → 200 + Content-Type: text/plain"""
    response = requests.get(f"{API_URL}/metrics")

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/plain")

    # Vérifier que ça ressemble à des métriques Prometheus
    content = response.text
    assert "# HELP" in content or "# TYPE" in content


if __name__ == "__main__":
    # Permet d'exécuter directement le fichier pour debug
    pytest.main([__file__, "-v"])
