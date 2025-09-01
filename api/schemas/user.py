from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from .base import BaseSchema, IDSchema
from models.user import UserRole
from utils.password import validate_password_policy

class UserBase(BaseSchema):
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    localisation: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Valide la politique de mot de passe CNIL"""
        is_valid, errors = validate_password_policy(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v

class UserUpdate(BaseSchema):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    localisation: Optional[str] = None
    password: Optional[str] = None
    
    @field_validator('password')
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
        return f"{self.prenom} {self.nom}"

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
