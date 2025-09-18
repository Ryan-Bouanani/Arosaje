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
        # Gestion de la compatibilité entre anciens et nouveaux champs
        first_name = obj_in.first_name or obj_in.prenom or ''
        last_name = obj_in.last_name or obj_in.nom or ''
        location = obj_in.location or obj_in.localisation
        
        db_obj = User(
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
            # Nouveaux champs anglais
            first_name=first_name,
            last_name=last_name,
            location=location,
            telephone=obj_in.telephone,
            role=obj_in.role,
            # Anciens champs français pour compatibilité
            nom=obj_in.nom or last_name,
            prenom=obj_in.prenom or first_name,
            localisation=obj_in.localisation or location,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in) -> User:
        """Mettre à jour un utilisateur avec les données fournies"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
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
