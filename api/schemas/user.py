from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from .base import BaseSchema, IDSchema
from models.user import UserRole
from utils.password import validate_password_policy


class UserBase(BaseSchema):
    # Champs anglais (standard technique)
    first_name: str
    last_name: str
    email: EmailStr
    telephone: Optional[str] = None
    location: Optional[str] = None
    
    # Propriétés calculées pour compatibilité temporaire
    @property
    def computed_first_name(self) -> str:
        return self.first_name or self.prenom or ''
    
    @property
    def computed_last_name(self) -> str:
        return self.last_name or self.nom or ''


class UserCreate(BaseSchema):
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.USER
    # Champs anglais requis
    first_name: str
    last_name: str
    telephone: Optional[str] = None
    location: Optional[str] = None
    # Support temporaire des anciens champs pour compatibilité API
    nom: Optional[str] = None
    prenom: Optional[str] = None
    localisation: Optional[str] = None
    
    # Validation pour s'assurer qu'au moins un format est fourni
    @field_validator('first_name')
    @classmethod
    def validate_names(cls, v, info):
        # Vérifier qu'on a soit first_name/last_name soit prenom/nom
        if not v and not info.data.get('prenom'):
            if not info.data.get('last_name') and not info.data.get('nom'):
                raise ValueError('Either first_name/last_name or prenom/nom must be provided')
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Valide la politique de mot de passe CNIL"""
        is_valid, errors = validate_password_policy(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v


class UserUpdate(BaseSchema):
    # Nouveaux champs anglais
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    location: Optional[str] = None
    # Anciens champs français (compatibilité temporaire)
    nom: Optional[str] = None
    prenom: Optional[str] = None
    localisation: Optional[str] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Valide la politique de mot de passe CNIL si le mot de passe est fourni"""
        if v is not None:
            is_valid, errors = validate_password_policy(v)
            if not is_valid:
                raise ValueError("; ".join(errors))
        return v


class UserRoleUpdate(BaseModel):
    role: UserRole


class User(UserBase, IDSchema):
    id: int
    role: UserRole

    @property
    def username(self) -> str:
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.first_name or self.prenom} {self.last_name or self.nom}"

    @property
    def name(self) -> str:
        """Alias pour username pour la compatibilité"""
        return self.username

    class Config:
        from_attributes = True


class UserInDB(User):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
