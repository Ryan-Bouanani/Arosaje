import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from unittest.mock import Mock

from models.refresh_token import RefreshToken
from models.user import User, UserRole
from utils.security import create_tokens, verify_refresh_token, revoke_user_tokens, cleanup_expired_tokens
from crud.user import user as user_crud
from schemas.user import UserCreate


class TestRefreshTokenModel:
    """Tests pour le modèle RefreshToken"""
    
    def test_generate_token_uniqueness(self):
        """Test que les tokens générés sont uniques"""
        token1 = RefreshToken.generate_token()
        token2 = RefreshToken.generate_token()
        
        assert token1 != token2
        assert len(token1) == 64  # 48 bytes en base64url = 64 chars
        assert len(token2) == 64
    
    def test_create_for_user(self):
        """Test de création d'un token pour un utilisateur"""
        token_obj = RefreshToken.create_for_user(
            user_id=1,
            expires_in_days=7,
            device_info="Test device"
        )
        
        assert token_obj.user_id == 1
        assert token_obj.device_info == "Test device"
        assert token_obj.is_revoked == False
        assert token_obj.expires_at > datetime.utcnow()
        assert token_obj.last_used_at is not None
    
    def test_is_expired(self):
        """Test de vérification d'expiration"""
        # Token non expiré
        token_valid = RefreshToken.create_for_user(user_id=1, expires_in_days=1)
        assert not token_valid.is_expired()
        
        # Token expiré
        token_expired = RefreshToken.create_for_user(user_id=1, expires_in_days=1)
        token_expired.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert token_expired.is_expired()
    
    def test_is_valid(self):
        """Test de validation complète du token"""
        token = RefreshToken.create_for_user(user_id=1, expires_in_days=1)
        
        # Token valide
        assert token.is_valid()
        
        # Token révoqué
        token.revoke()
        assert not token.is_valid()
        
        # Token expiré
        token.is_revoked = False
        token.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert not token.is_valid()
    
    def test_revoke(self):
        """Test de révocation d'un token"""
        token = RefreshToken.create_for_user(user_id=1, expires_in_days=1)
        assert not token.is_revoked
        
        token.revoke()
        assert token.is_revoked
        assert not token.is_valid()


class TestRefreshTokenSecurity:
    """Tests pour les fonctions de sécurité des refresh tokens"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de base de données"""
        db = Mock(spec=Session)
        return db
    
    @pytest.fixture
    def test_user(self, mock_db):
        """Utilisateur de test"""
        user = User(
            id=1,
            email="test@example.com",
            password="hashed_password",
            nom="Test",
            prenom="User",
            role=UserRole.USER,
            is_verified=True
        )
        return user
    
    def test_create_tokens(self, mock_db, test_user):
        """Test de création de tokens"""
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        access_token, refresh_token = create_tokens(test_user.id, mock_db)
        
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert len(refresh_token) == 64
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_verify_refresh_token_valid(self, mock_db):
        """Test de vérification d'un token valide"""
        valid_token = RefreshToken.create_for_user(user_id=1, expires_in_days=7)
        mock_db.query.return_value.filter.return_value.first.return_value = valid_token
        mock_db.commit.return_value = None
        
        result = verify_refresh_token("valid_token", mock_db)
        
        assert result == valid_token
        mock_db.commit.assert_called_once()
    
    def test_verify_refresh_token_invalid(self, mock_db):
        """Test de vérification d'un token invalide"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = verify_refresh_token("invalid_token", mock_db)
        
        assert result is None
    
    def test_verify_refresh_token_revoked(self, mock_db):
        """Test de vérification d'un token révoqué"""
        revoked_token = RefreshToken.create_for_user(user_id=1, expires_in_days=7)
        revoked_token.revoke()
        mock_db.query.return_value.filter.return_value.first.return_value = revoked_token
        
        result = verify_refresh_token("revoked_token", mock_db)
        
        assert result is None
    
    def test_revoke_user_tokens(self, mock_db):
        """Test de révocation des tokens d'un utilisateur"""
        token1 = RefreshToken.create_for_user(user_id=1, expires_in_days=7)
        token2 = RefreshToken.create_for_user(user_id=1, expires_in_days=7)
        
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [token1, token2]
        mock_db.commit.return_value = None
        
        revoke_user_tokens(1, mock_db)
        
        assert token1.is_revoked
        assert token2.is_revoked
        mock_db.commit.assert_called_once()
    
    def test_cleanup_expired_tokens(self, mock_db):
        """Test de nettoyage des tokens expirés"""
        expired_token1 = RefreshToken.create_for_user(user_id=1, expires_in_days=1)
        expired_token1.expires_at = datetime.utcnow() - timedelta(hours=1)
        
        expired_token2 = RefreshToken.create_for_user(user_id=2, expires_in_days=1)
        expired_token2.expires_at = datetime.utcnow() - timedelta(days=1)
        
        mock_db.query.return_value.filter.return_value.all.return_value = [expired_token1, expired_token2]
        mock_db.delete.return_value = None
        mock_db.commit.return_value = None
        
        count = cleanup_expired_tokens(mock_db)
        
        assert count == 2
        assert mock_db.delete.call_count == 2
        mock_db.commit.assert_called_once()


class TestTokenSecurity:
    """Tests de sécurité pour les tokens"""
    
    def test_token_entropy(self):
        """Test que les tokens ont une entropie suffisante"""
        tokens = [RefreshToken.generate_token() for _ in range(100)]
        
        # Vérifier l'unicité
        assert len(set(tokens)) == 100
        
        # Vérifier la distribution des caractères
        all_chars = ''.join(tokens)
        char_counts = {}
        for char in all_chars:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Aucun caractère ne devrait représenter plus de 5% du total
        max_frequency = max(char_counts.values()) / len(all_chars)
        assert max_frequency < 0.05
    
    def test_token_format(self):
        """Test que les tokens respectent le format attendu"""
        token = RefreshToken.generate_token()
        
        # Doit être en base64url (pas de +, /, ou =)
        assert '+' not in token
        assert '/' not in token
        assert '=' not in token
        
        # Doit contenir seulement des caractères alphanumériques, -, _
        import re
        assert re.match(r'^[A-Za-z0-9_-]+$', token)


if __name__ == "__main__":
    pytest.main([__file__])