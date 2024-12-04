from pydantic import BaseModel

class UserBase(BaseModel):
    nom: str
    prenom: str
    email: str
    telephone: str | None = None
    role: str
    localisation: str | None = None

class UserCreate(UserBase):
    mot_de_passe: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True
