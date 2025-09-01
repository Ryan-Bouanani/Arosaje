"""
Tests unitaires pour les utilitaires de sécurité JWT
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from utils.security import create_access_token
from jose import jwt


class TestSecurityUtils:
    """Tests pour les fonctions JWT"""
    
    @patch('utils.security.SECRET_KEY', 'test_secret_key')
    @patch('utils.security.ALGORITHM', 'HS256')
    def test_create_access_token(self):
        """Test de création de token JWT"""
        data = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT fait généralement plus de 50 chars
    
    @patch('utils.security.SECRET_KEY', 'test_secret_key')
    @patch('utils.security.ALGORITHM', 'HS256')
    def test_create_access_token_with_expiry(self):
        """Test de création de token avec expiration personnalisée"""
        data = {"sub": "test@example.com", "role": "user"}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta)
        
        assert token is not None
        
        # Décoder manuellement pour vérifier que le token contient une expiration
        decoded = jwt.decode(token, 'test_secret_key', algorithms=['HS256'])
        assert 'exp' in decoded
        assert 'sub' in decoded
        assert decoded['sub'] == data['sub']
    
    @patch('utils.security.SECRET_KEY', 'test_secret_key')
    @patch('utils.security.ALGORITHM', 'HS256')
    def test_decode_valid_token(self):
        """Test de décodage d'un token valide"""
        original_data = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(original_data)
        
        # Décoder manuellement le token
        decoded_data = jwt.decode(token, 'test_secret_key', algorithms=['HS256'])
        
        assert decoded_data is not None
        assert decoded_data["sub"] == original_data["sub"]
        assert decoded_data["role"] == original_data["role"]
        assert "exp" in decoded_data  # L'expiration doit être ajoutée
    
    @patch('utils.security.SECRET_KEY', 'test_secret_key')
    @patch('utils.security.ALGORITHM', 'HS256')
    def test_decode_invalid_token(self):
        """Test de décodage d'un token invalide"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):  # JWT decode error
            jwt.decode(invalid_token, 'test_secret_key', algorithms=['HS256'])
    
    @patch('utils.security.SECRET_KEY', 'test_secret_key')
    @patch('utils.security.ALGORITHM', 'HS256')
    def test_decode_expired_token(self):
        """Test de décodage d'un token expiré"""
        data = {"sub": "test@example.com", "role": "user"}
        # Créer un token qui expire immédiatement
        expired_token = create_access_token(data, timedelta(seconds=-10))
        
        with pytest.raises(Exception):  # JWT expired error
            jwt.decode(expired_token, 'test_secret_key', algorithms=['HS256'])
    
    @patch('utils.security.SECRET_KEY', 'test_secret_key')
    @patch('utils.security.ALGORITHM', 'HS256')
    def test_token_with_wrong_secret(self):
        """Test de décodage avec une mauvaise clé secrète"""
        data = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(data)
        
        # Essayer de décoder avec une mauvaise clé
        with pytest.raises(Exception):  # JWT signature error
            jwt.decode(token, 'wrong_secret_key', algorithms=['HS256'])