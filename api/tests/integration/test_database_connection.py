"""
Tests d'intégration pour la base de données
"""

import pytest
from sqlalchemy import text
from utils.database import get_db


class TestDatabaseIntegration:
    """Tests d'intégration avec la base de données"""

    def test_database_connection(self):
        """Test de connexion à la base de données"""
        # Utilise une DB de test ou la DB existante selon la configuration
        db_gen = get_db()
        db = next(db_gen)

        try:
            # Test de requête basique
            result = db.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row[0] == 1
        finally:
            db.close()

    def test_database_tables_exist(self):
        """Test que les tables principales existent"""
        db_gen = get_db()
        db = next(db_gen)

        try:
            # Vérifier que les tables principales existent
            tables_to_check = [
                "users",
                "plants",
                "plant_cares",
                "messages",
                "care_reports",
            ]

            for table in tables_to_check:
                result = db.execute(
                    text(
                        f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    );
                """
                    )
                )
                exists = result.fetchone()[0]
                assert exists, f"Table {table} n'existe pas"

        finally:
            db.close()

    def test_database_crud_operations(self):
        """Test des opérations CRUD basiques sur la DB"""
        from models.user import User, UserRole

        db_gen = get_db()
        db = next(db_gen)

        try:
            # Test d'insertion
            test_user = User(
                nom="TestUser",
                prenom="Integration",
                email=f"test_integration_{id(db)}@example.com",
                telephone="0123456789",
                localisation="Test City",
                password="test_hash",
                role=UserRole.USER,
                is_verified=True,
            )

            db.add(test_user)
            db.commit()
            db.refresh(test_user)

            assert test_user.id is not None

            # Test de lecture
            retrieved_user = db.query(User).filter(User.id == test_user.id).first()
            assert retrieved_user is not None
            assert retrieved_user.nom == "TestUser"
            assert retrieved_user.email == test_user.email

            # Test de mise à jour
            retrieved_user.nom = "UpdatedTestUser"
            db.commit()

            updated_user = db.query(User).filter(User.id == test_user.id).first()
            assert updated_user.nom == "UpdatedTestUser"

            # Test de suppression
            db.delete(updated_user)
            db.commit()

            deleted_user = db.query(User).filter(User.id == test_user.id).first()
            assert deleted_user is None

        finally:
            db.close()

    def test_database_constraints(self):
        """Test des contraintes de base de données"""
        from models.user import User, UserRole

        db_gen = get_db()
        db = next(db_gen)

        try:
            # Test de contrainte d'unicité sur l'email
            unique_email = f"unique_test_{id(db)}@example.com"

            user1 = User(
                nom="User1",
                prenom="Test",
                email=unique_email,
                telephone="0123456789",
                localisation="Test City",
                password="test_hash",
                role=UserRole.USER,
            )

            db.add(user1)
            db.commit()

            # Essayer d'insérer un deuxième utilisateur avec le même email
            user2 = User(
                nom="User2",
                prenom="Test",
                email=unique_email,  # Même email
                telephone="0123456789",
                localisation="Test City",
                password="test_hash",
                role=UserRole.USER,
            )

            db.add(user2)

            # Cela devrait lever une exception
            with pytest.raises(Exception):  # IntegrityError ou similaire
                db.commit()

            db.rollback()

            # Nettoyer
            db.delete(user1)
            db.commit()

        finally:
            db.close()
