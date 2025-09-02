from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from utils.database import Base
import enum


class AdvicePriority(str, enum.Enum):
    NORMAL = "normal"
    URGENT = "urgent"
    FOLLOW_UP = "follow_up"


class ValidationStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class Advice(Base):
    __tablename__ = "advices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_care_id = Column(
        Integer, ForeignKey("plant_cares.id", ondelete="CASCADE"), nullable=False
    )
    botanist_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Contenu de l'avis
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(Enum(AdvicePriority), default=AdvicePriority.NORMAL)

    # Système de validation
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.PENDING)
    validator_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    validation_comment = Column(Text, nullable=True)
    validated_at = Column(DateTime, nullable=True)

    # Version et historique
    version = Column(Integer, default=1)
    is_current_version = Column(Boolean, default=True)
    previous_version_id = Column(
        Integer, ForeignKey("advices.id", ondelete="SET NULL"), nullable=True
    )

    # Notifications
    owner_notified = Column(Boolean, default=False)
    botanist_notified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    plant_care = relationship("PlantCare", back_populates="botanist_advice")
    botanist = relationship(
        "User", foreign_keys=[botanist_id], back_populates="given_advice"
    )
    validator = relationship(
        "User", foreign_keys=[validator_id], back_populates="validated_advice"
    )
    previous_version = relationship(
        "Advice", remote_side=[id], back_populates="updated_versions"
    )
    updated_versions = relationship("Advice", back_populates="previous_version")

    def to_dict(self):
        """Convertit l'objet en dictionnaire sérialisable"""
        botanist_info = None
        if self.botanist:
            botanist_info = {
                "id": self.botanist.id,
                "prenom": self.botanist.prenom,
                "nom": self.botanist.nom,
                "email": self.botanist.email,
            }

        validator_info = None
        if self.validator:
            validator_info = {
                "id": self.validator.id,
                "prenom": self.validator.prenom,
                "nom": self.validator.nom,
                "email": self.validator.email,
            }

        return {
            "id": self.id,
            "plant_care_id": self.plant_care_id,
            "botanist_id": self.botanist_id,
            "title": self.title,
            "content": self.content,
            "priority": self.priority.value if self.priority else "normal",
            "validation_status": (
                self.validation_status.value if self.validation_status else "pending"
            ),
            "validator_id": self.validator_id,
            "validation_comment": self.validation_comment,
            "validated_at": (
                self.validated_at.isoformat() if self.validated_at else None
            ),
            "version": self.version,
            "is_current_version": self.is_current_version,
            "previous_version_id": self.previous_version_id,
            "owner_notified": self.owner_notified,
            "botanist_notified": self.botanist_notified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "botanist": botanist_info,
            "validator": validator_info,
        }
