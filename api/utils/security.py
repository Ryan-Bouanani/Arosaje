from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from utils.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from utils.database import get_db
from crud.user import user as user_crud
from schemas.token import TokenData
from models.refresh_token import RefreshToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Optional[dict]:
    """Récupère l'utilisateur actuel à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    user = user_crud.get(db, id=int(token_data.user_id))
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user=Security(get_current_user)):
    """Vérifie que l'utilisateur est actif"""
    return current_user


async def get_current_user_ws(token: str, db: Session) -> dict:
    """
    Authentifie un utilisateur via son token JWT pour les WebSockets
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_crud.get(db, id=int(user_id))
    if user is None:
        raise credentials_exception
    return user


def create_tokens(user_id: int, db: Session, request: Request = None) -> Tuple[str, str]:
    """
    Crée à la fois un access token et un refresh token pour un utilisateur
    """
    # Créer l'access token
    access_token = create_access_token(data={"sub": str(user_id)})
    
    # Extraire les informations du device si possible
    device_info = None
    if request:
        user_agent = request.headers.get("user-agent", "")
        client_ip = request.client.host if request.client else "unknown"
        device_info = f"IP:{client_ip} UA:{user_agent[:200]}"  # Limiter à 200 chars
    
    # Créer le refresh token
    refresh_token_obj = RefreshToken.create_for_user(
        user_id=user_id,
        expires_in_days=REFRESH_TOKEN_EXPIRE_DAYS,
        device_info=device_info
    )
    
    # Sauvegarder en base
    db.add(refresh_token_obj)
    db.commit()
    db.refresh(refresh_token_obj)
    
    return access_token, refresh_token_obj.token


def verify_refresh_token(refresh_token: str, db: Session) -> Optional[RefreshToken]:
    """
    Vérifie et retourne un refresh token s'il est valide
    """
    token_obj = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()
    
    if not token_obj or not token_obj.is_valid():
        return None
    
    # Mettre à jour la date de dernière utilisation
    token_obj.update_last_used()
    db.commit()
    
    return token_obj


def revoke_user_tokens(user_id: int, db: Session, except_token: str = None) -> None:
    """
    Révoque tous les tokens d'un utilisateur (sauf celui spécifié)
    """
    query = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    )
    
    if except_token:
        query = query.filter(RefreshToken.token != except_token)
    
    tokens = query.all()
    for token in tokens:
        token.revoke()
    
    db.commit()


def cleanup_expired_tokens(db: Session) -> int:
    """
    Nettoie les tokens expirés de la base de données
    Retourne le nombre de tokens supprimés
    """
    expired_tokens = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.now(timezone.utc)
    ).all()
    
    count = len(expired_tokens)
    for token in expired_tokens:
        db.delete(token)
    
    db.commit()
    return count
