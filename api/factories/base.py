"""
Factory de base pour A'rosa-je
Fournit la configuration commune à toutes les factories
"""

import factory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Configuration database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_YfAhut3ZEMS2@ep-spring-bonus-agd7s9t1-pooler.c-2.eu-central-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require')

# Session SQLAlchemy partagée
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Factory de base pour tous les modèles A'rosa-je
    Configure automatiquement la session SQLAlchemy et les paramètres communs
    """

    class Meta:
        abstract = True
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Création personnalisée avec gestion d'erreurs et merge des objets
        """
        try:
            # Merger les objets qui pourraient venir d'autres sessions
            for key, value in kwargs.items():
                if hasattr(value, '__table__'):  # Si c'est un objet SQLAlchemy
                    # Merger l'objet dans la session actuelle
                    kwargs[key] = cls._meta.sqlalchemy_session.merge(value)

            return super()._create(model_class, *args, **kwargs)
        except Exception as e:
            # Rollback en cas d'erreur
            cls._meta.sqlalchemy_session.rollback()
            raise e

    @classmethod
    def _get_or_create_user_by_email(cls, email):
        """
        Récupère un utilisateur existant par email ou retourne None
        Utilise la session de la factory pour éviter les conflits
        """
        from models.user import User
        return cls._meta.sqlalchemy_session.query(User).filter(User.email == email).first()

    @classmethod
    def create_batch_safe(cls, size, **kwargs):
        """
        Création de batch avec gestion d'erreurs et commit par lot
        Plus efficace pour de grosses quantités
        """
        objects = []
        try:
            for i in range(size):
                obj = cls.build(**kwargs)
                cls._meta.sqlalchemy_session.add(obj)
                objects.append(obj)

                # Commit par lot de 50 pour éviter les timeouts
                if (i + 1) % 50 == 0:
                    cls._meta.sqlalchemy_session.commit()

            # Commit final pour les objets restants
            cls._meta.sqlalchemy_session.commit()
            return objects

        except Exception as e:
            cls._meta.sqlalchemy_session.rollback()
            raise e

class ImageMixin:
    """
    Mixin pour gérer les images base64
    """

    @staticmethod
    def image_to_base64(image_path):
        """Convertit une image en data URL base64"""
        import base64
        try:
            with open(image_path, 'rb') as f:
                data = f.read()

            ext = os.path.splitext(image_path)[1].lower()
            mime_type = 'image/jpeg' if ext == '.jpg' else 'image/png'
            b64_data = base64.b64encode(data).decode('utf-8')
            return f'data:{mime_type};base64,{b64_data}'
        except Exception as e:
            print(f'Erreur conversion image {image_path}: {e}')
            return 'data:image/jpeg;base64,placeholder'

# Export pour usage facile
__all__ = ['BaseFactory', 'ImageMixin', 'SessionLocal']