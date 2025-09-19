"""
Seeders modernisés pour A'rosa-je avec factory_boy + Faker
Architecture modulaire et CLI avancée
"""

from abc import ABC, abstractmethod
import time
from sqlalchemy import text
from factories.base import SessionLocal

class BaseSeeder(ABC):
    """
    Classe de base pour tous les seeders
    Fournit les méthodes communes et l'interface standardisée
    """

    def __init__(self):
        self.session = SessionLocal()
        self.created_count = 0
        self.start_time = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    @abstractmethod
    def seed(self, count=10, **kwargs):
        """Méthode principale de seeding à implémenter"""
        pass

    @abstractmethod
    def clear(self):
        """Nettoie les données de ce seeder"""
        pass

    def start_timer(self):
        """Démarre le chronométrage"""
        self.start_time = time.time()

    def end_timer(self):
        """Termine le chronométrage et affiche le résultat"""
        if self.start_time:
            duration = time.time() - self.start_time
            print(f"  OK {self.created_count} entités créées en {duration:.2f}s")

    def safe_execute(self, sql, description="operation"):
        """Exécute une requête SQL avec gestion d'erreurs"""
        try:
            self.session.execute(text(sql))
            self.session.commit()
            print(f"  OK {description}")
        except Exception as e:
            self.session.rollback()
            print(f"  ERREUR {description}: {e}")

class Statistics:
    """Utilitaire pour afficher les statistiques de la base"""

    @staticmethod
    def show_database_stats():
        """Affiche les statistiques actuelles de la base"""
        with SessionLocal() as session:
            tables = [
                ('users', 'utilisateurs'),
                ('plants', 'plantes'),
                ('plant_cares', 'gardes'),
                ('advices', 'conseils'),
                ('care_reports', 'rapports')
            ]

            print("\nStatistiques de la base de donnees:")
            total = 0

            for table, label in tables:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"  {label.capitalize()}: {result}")
                    total += result
                except Exception as e:
                    print(f"  {label.capitalize()}: Erreur ({e})")

            print(f"  TOTAL: {total} entités")

# Exports
__all__ = ['BaseSeeder', 'Statistics']