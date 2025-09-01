"""
Tests unitaires pour les utilitaires de mot de passe
"""
import pytest
from utils.password import get_password_hash, verify_password


class TestPasswordUtils:
    """Tests pour les fonctions de hachage de mot de passe"""
    
    def test_hash_password(self):
        """Test du hachage de mot de passe"""
        password = "test123secure"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 50  # Hash bcrypt fait au moins 60 chars
        assert hashed != password  # Le hash ne doit pas être identique au mot de passe
    
    def test_verify_password_success(self):
        """Test de vérification de mot de passe correct"""
        password = "test123secure"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        """Test de vérification de mot de passe incorrect"""
        password = "test123secure"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_different_passwords_produce_different_hashes(self):
        """Test que des mots de passe différents produisent des hash différents"""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2
    
    def test_hash_same_password_produces_different_salts(self):
        """Test que le même mot de passe produit des hash différents (salt aléatoire)"""
        password = "samepassword"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Différents hashs mais tous deux valides pour le même mot de passe
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_empty_password(self):
        """Test avec mot de passe vide"""
        password = ""
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is True
        assert verify_password("nonempty", hashed) is False