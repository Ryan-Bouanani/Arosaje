from pydantic import BaseModel, EmailStr
from typing import Optional
from .base import BaseSchema, IDSchema
from models.user import UserRole

class UserBase(BaseSchema):
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    localisation: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseSchema):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    localisation: Optional[str] = None
    password: Optional[str] = None

class UserRoleUpdate(BaseModel):
    role: UserRole

class User(UserBase, IDSchema):
    id: int
    role: UserRole

    class Config:
        from_attributes = True

class UserInDB(User):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
