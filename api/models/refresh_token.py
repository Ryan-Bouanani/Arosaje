from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import secrets
from utils.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Informations de traçabilité
    device_info = Column(String(500), nullable=True)  # User-Agent, device info
    last_used_at = Column(DateTime, nullable=True)

    # Relations
    user = relationship("User", back_populates="refresh_tokens")

    @classmethod
    def generate_token(cls) -> str:
        """Génère un token sécurisé de 64 caractères"""
        return secrets.token_urlsafe(48)  # 48 bytes = 64 chars en base64url

    @classmethod
    def create_for_user(
        cls, 
        user_id: int, 
        expires_in_days: int = 7, 
        device_info: str = None
    ) -> "RefreshToken":
        """Crée un nouveau refresh token pour un utilisateur"""
        token = cls.generate_token()
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        return cls(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            device_info=device_info,
            last_used_at=datetime.utcnow()
        )

    def is_expired(self) -> bool:
        """Vérifie si le token a expiré"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Vérifie si le token est valide (non révoqué et non expiré)"""
        return not self.is_revoked and not self.is_expired()

    def revoke(self) -> None:
        """Révoque le token"""
        self.is_revoked = True
        self.updated_at = datetime.utcnow()

    def update_last_used(self) -> None:
        """Met à jour la date de dernière utilisation"""
        self.last_used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "id": self.id,
            "token": self.token,
            "user_id": self.user_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_revoked": self.is_revoked,
            "device_info": self.device_info,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }