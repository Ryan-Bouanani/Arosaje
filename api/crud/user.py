from typing import Optional
from sqlalchemy.orm import Session
from models.user import User, UserRole
from schemas.user import UserCreate
from utils.password import get_password_hash

class CRUDUser:
    def get(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
            nom=obj_in.nom,
            prenom=obj_in.prenom,
            telephone=obj_in.telephone,
            localisation=obj_in.localisation,
            role=obj_in.role
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_role(self, db: Session, *, db_obj: User, role: UserRole) -> User:
        db_obj.role = role
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user = CRUDUser() 