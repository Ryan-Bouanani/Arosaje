import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from utils.database import get_db, Base
from models.user import User, UserRole
from models.refresh_token import RefreshToken
from utils.password import get_password_hash


# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_refresh_token.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestRefreshTokenFlow:
    """Tests d'intégration pour le flow refresh token complet"""
    
    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Configurer la base de données pour chaque test"""
        Base.metadata.create_all(bind=engine)
        
        # Créer un utilisateur de test
        db = TestingSessionLocal()
        test_user = User(
            email="test@example.com",
            password=get_password_hash("testpassword"),
            first_name="User",
            last_name="Test",
            role=UserRole.USER,
            is_verified=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        db.close()
        
        yield
        
        # Nettoyer après chaque test
        Base.metadata.drop_all(bind=engine)
    
    def test_login_returns_both_tokens(self):
        """Test que le login retourne access_token ET refresh_token"""
        response = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la présence des deux tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Vérifier que les tokens ne sont pas vides
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
        
        # Vérifier que le refresh_token est bien stocké en base
        db = TestingSessionLocal()
        refresh_token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == data["refresh_token"]
        ).first()
        
        assert refresh_token_obj is not None
        assert refresh_token_obj.user_id == 1
        assert refresh_token_obj.is_valid()
        db.close()
    
    def test_refresh_token_generates_new_access_token(self):
        """Test que le refresh token génère un nouveau access token"""
        # 1. Login pour obtenir les tokens
        login_response = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        original_access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]
        
        # 2. Utiliser le refresh token pour obtenir un nouveau access token
        refresh_response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        
        # 3. Vérifier que le nouveau access token est différent
        new_access_token = refresh_data["access_token"]
        assert new_access_token != original_access_token
        assert refresh_data["token_type"] == "bearer"
    
    def test_refresh_token_with_invalid_token_fails(self):
        """Test que l'utilisation d'un refresh token invalide échoue"""
        response = client.post("/auth/refresh", json={
            "refresh_token": "invalid_token_12345"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "invalide" in data["detail"].lower()
    
    def test_refresh_token_updates_last_used(self):
        """Test que l'utilisation du refresh token met à jour last_used_at"""
        # 1. Login
        login_response = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # 2. Vérifier l'état initial
        db = TestingSessionLocal()
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        initial_last_used = token_obj.last_used_at
        db.close()
        
        # 3. Attendre un peu et utiliser le refresh token
        import time
        time.sleep(1)
        
        client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        # 4. Vérifier que last_used_at a été mis à jour
        db = TestingSessionLocal()
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        final_last_used = token_obj.last_used_at
        db.close()
        
        assert final_last_used > initial_last_used
    
    def test_access_with_new_token_works(self):
        """Test que le nouveau access token permet d'accéder aux endpoints protégés"""
        # 1. Login
        login_response = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # 2. Obtenir un nouveau access token
        refresh_response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        new_access_token = refresh_response.json()["access_token"]
        
        # 3. Utiliser le nouveau token pour accéder au profil
        profile_response = client.get("/auth/me", headers={
            "Authorization": f"Bearer {new_access_token}"
        })
        
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["email"] == "test@example.com"
    
    def test_expired_refresh_token_fails(self):
        """Test qu'un refresh token expiré ne fonctionne pas"""
        # 1. Login
        login_response = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # 2. Marquer le token comme expiré en base
        db = TestingSessionLocal()
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        token_obj.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db.commit()
        db.close()
        
        # 3. Tenter d'utiliser le token expiré
        response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 401
    
    def test_revoked_refresh_token_fails(self):
        """Test qu'un refresh token révoqué ne fonctionne pas"""
        # 1. Login
        login_response = client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # 2. Révoquer le token en base
        db = TestingSessionLocal()
        token_obj = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        token_obj.revoke()
        db.commit()
        db.close()
        
        # 3. Tenter d'utiliser le token révoqué
        response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 401
    
    def test_multiple_refresh_tokens_per_user(self):
        """Test qu'un utilisateur peut avoir plusieurs refresh tokens actifs"""
        # Simuler plusieurs logins (différents devices)
        responses = []
        for i in range(3):
            response = client.post("/auth/login", data={
                "username": "test@example.com",
                "password": "testpassword"
            })
            responses.append(response.json())
        
        # Vérifier qu'on a 3 refresh tokens différents
        refresh_tokens = [r["refresh_token"] for r in responses]
        assert len(set(refresh_tokens)) == 3
        
        # Vérifier que tous les tokens fonctionnent
        for token in refresh_tokens:
            response = client.post("/auth/refresh", json={
                "refresh_token": token
            })
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])