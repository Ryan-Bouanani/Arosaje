from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: str | None = None
    localisation: str | None = None

class UserCreate(UserBase):
    mot_de_passe: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str
