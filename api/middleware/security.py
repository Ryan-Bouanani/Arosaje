"""
Middleware global de sécurité pour l'API A'rosa-je
Gère l'authentification automatique sur toutes les routes privées
"""
import re
from typing import Set
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from utils.settings import SECRET_KEY, ALGORITHM
from utils.database import SessionLocal
from crud.user import user as user_crud
from utils.security import oauth2_scheme
from models.user import UserRole


class SecurityMiddleware:
    """
    Middleware de sécurité centralisé
    Équivalent du security.yml de Symfony
    """

    # Routes publiques (pas d'authentification requise)
    PUBLIC_ROUTES: Set[str] = {
        # Authentification
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
        "/auth/verify-email",
        "/auth/reset-password",

        # Documentation
        "/docs",
        "/redoc",
        "/openapi.json",

        # Santé et monitoring
        "/health",
        "/",

        # WebSocket (authentification gérée séparément)
        "/ws",

        # Assets statiques
        "/static",

        # Geocoding (autocomplétion d'adresses)
        "/geocoding/autocomplete",
        "/geocoding/geocode",
    }

    # Patterns de routes publiques (regex)
    PUBLIC_PATTERNS = [
        r"^/static/.*$",       # Tous les assets statiques
        r"^/ws.*$",            # Tous les WebSockets
        r"^/docs.*$",          # Documentation
        r"^/redoc.*$",         # Documentation alternative
    ]

    def __init__(self):
        """Initialise le middleware"""
        self.compiled_patterns = [re.compile(pattern) for pattern in self.PUBLIC_PATTERNS]

    def is_public_route(self, path: str) -> bool:
        """
        Détermine si une route est publique

        Args:
            path: Chemin de la requête

        Returns:
            bool: True si la route est publique
        """
        # Vérification dans les routes exactes
        if path in self.PUBLIC_ROUTES:
            return True

        # Vérification avec les patterns regex
        for pattern in self.compiled_patterns:
            if pattern.match(path):
                return True

        return False

    def extract_token_from_header(self, authorization: str) -> str:
        """
        Extrait le token JWT du header Authorization

        Args:
            authorization: Header Authorization complet

        Returns:
            str: Token JWT extrait

        Raises:
            HTTPException: Si le format est invalide
        """
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Header Authorization manquant"
            )

        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Format du token invalide. Utilisez: Bearer <token>"
            )

        return authorization.replace("Bearer ", "")

    def validate_jwt_token(self, token: str, db: Session) -> dict:
        """
        Valide un token JWT et retourne les informations utilisateur

        Args:
            token: Token JWT à valider
            db: Session de base de données

        Returns:
            dict: Informations de l'utilisateur

        Raises:
            HTTPException: Si le token est invalide ou l'utilisateur n'existe pas
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Décoder le token JWT
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")

            if user_id is None:
                raise credentials_exception

        except JWTError:
            raise credentials_exception

        # Vérifier que l'utilisateur existe en base
        user = user_crud.get(db, id=int(user_id))
        if user is None:
            raise credentials_exception

        return user

    async def __call__(self, request: Request, call_next):
        """
        Middleware principal - traite chaque requête
        Équivalent des access_control de Symfony
        """
        path = request.url.path
        method = request.method

        # OPTIONS pour CORS - toujours autoriser
        if method == "OPTIONS":
            return await call_next(request)

        # Route publique - passer sans vérification
        if self.is_public_route(path):
            return await call_next(request)

        # Route privée - vérifier l'authentification
        try:
            # Récupérer le header Authorization
            authorization = request.headers.get("authorization")
            token = self.extract_token_from_header(authorization)

            # Valider le token JWT
            db = SessionLocal()
            try:
                user = self.validate_jwt_token(token, db)

                # Ajouter l'utilisateur au contexte de la requête
                # (utilisable dans les endpoints via request.state.user)
                request.state.user = user

                # Contrôle de rôle par path 
                if path.startswith("/admin"):
                    if user.role != UserRole.ADMIN:
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={"detail": "Accès réservé aux administrateurs"}
                        )

                elif path.startswith("/advices"):
                    # Lecture des conseils : accessible à tous
                    # Création des conseils : réservée aux botanistes
                    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                        if user.role not in [UserRole.BOTANIST, UserRole.ADMIN]:
                            return JSONResponse(
                                status_code=status.HTTP_403_FORBIDDEN,
                                content={"detail": "Création de conseils réservée aux botanistes"}
                            )
                    # GET autorisé pour tous les utilisateurs connectés

                elif path.startswith("/care-reports"):
                    # Lecture des rapports : accessible à tous
                    # Création des rapports : réservée aux gardiens et botanistes
                    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                        if user.role not in [UserRole.USER, UserRole.BOTANIST, UserRole.ADMIN]:
                            return JSONResponse(
                                status_code=status.HTTP_403_FORBIDDEN,
                                content={"detail": "Création de rapports réservée aux gardiens et botanistes"}
                            )
                    # GET autorisé pour tous les utilisateurs connectés

                elif path.startswith("/plant-care"):
                    # Gestion des gardes de plantes : accessible à tous les utilisateurs connectés
                    # Pas de restriction spéciale par rôle
                    pass

            finally:
                db.close()

        except HTTPException as e:
            # Retourner l'erreur d'authentification
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            # Erreur inattendue
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Erreur interne du serveur: {str(e)}"}
            )

        # Continuer vers l'endpoint
        response = await call_next(request)
        return response


# Instance globale du middleware
security_middleware = SecurityMiddleware()


async def global_security_middleware(request: Request, call_next):
    """
    Point d'entrée du middleware global de sécurité
    À ajouter dans main.py avec app.middleware("http")
    """
    return await security_middleware(request, call_next)