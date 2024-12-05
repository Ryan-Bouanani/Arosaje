from sqlalchemy.orm import Session
from models.user import User
from schemas.user_schema import UserCreate, UserLogin
from passlib.context import CryptContext

# Configurer PassLib pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    """Récupérer un utilisateur par email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """Créer un nouvel utilisateur."""
    hashed_password = pwd_context.hash(user.mot_de_passe)  # Hachage du mot de passe
    db_user = User(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email,
        telephone=user.telephone,
        localisation=user.localisation,
        mot_de_passe=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Supprimer un utilisateur par ID."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

def authenticate_user(db: Session, user_login: UserLogin):
    """Authentifier un utilisateur avec email et mot de passe."""
    db_user = get_user_by_email(db, user_login.email)
    if not db_user:
        return None
    if not pwd_context.verify(user_login.mot_de_passe, db_user.mot_de_passe):
        return None
    return db_user
