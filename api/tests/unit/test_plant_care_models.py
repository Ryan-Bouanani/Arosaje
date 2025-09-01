"""
Tests unitaires pour les modèles PlantCare et leurs relations
"""
import pytest
from datetime import datetime, timedelta
from models.plant_care import PlantCare, CareStatus
from models.user import User, UserRole
from models.plant import Plant


class TestPlantCareModels:
    """Tests pour les modèles de garde de plantes"""
    
    def test_plant_care_creation(self):
        """Test de création d'une garde de plante"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        plant_care = PlantCare(
            plant_id=1,
            owner_id=1,
            start_date=start_date,
            end_date=end_date,
            care_instructions="Arroser tous les 2 jours",
            status=CareStatus.PENDING
        )
        
        assert plant_care.plant_id == 1
        assert plant_care.owner_id == 1
        assert plant_care.start_date == start_date
        assert plant_care.end_date == end_date
        assert plant_care.care_instructions == "Arroser tous les 2 jours"
        assert plant_care.status == CareStatus.PENDING
        assert plant_care.caretaker_id is None  # Pas encore assigné
    
    def test_care_status_enum_values(self):
        """Test des valeurs de l'enum CareStatus"""
        assert CareStatus.PENDING.value == "pending"
        assert CareStatus.ACCEPTED.value == "accepted"
        assert CareStatus.IN_PROGRESS.value == "in_progress"
        assert CareStatus.COMPLETED.value == "completed"
        assert CareStatus.CANCELLED.value == "cancelled"
    
    def test_plant_care_status_transitions(self):
        """Test des transitions de statut"""
        plant_care = PlantCare(
            plant_id=1,
            owner_id=1,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
            status=CareStatus.PENDING
        )
        
        # Transition vers ACCEPTED
        plant_care.status = CareStatus.ACCEPTED
        plant_care.caretaker_id = 2
        assert plant_care.status == CareStatus.ACCEPTED
        assert plant_care.caretaker_id == 2
        
        # Transition vers IN_PROGRESS
        plant_care.status = CareStatus.IN_PROGRESS
        assert plant_care.status == CareStatus.IN_PROGRESS
        
        # Transition vers COMPLETED
        plant_care.status = CareStatus.COMPLETED
        assert plant_care.status == CareStatus.COMPLETED
    
    def test_plant_care_duration_calculation(self):
        """Test du calcul de durée de garde"""
        start_date = datetime(2024, 1, 1, 10, 0, 0)
        end_date = datetime(2024, 1, 8, 10, 0, 0)  # 7 jours exactement
        
        plant_care = PlantCare(
            plant_id=1,
            owner_id=1,
            start_date=start_date,
            end_date=end_date,
            status=CareStatus.PENDING
        )
        
        duration = plant_care.end_date - plant_care.start_date
        assert duration.days == 7
    
    def test_plant_care_is_active(self):
        """Test pour déterminer si une garde est active"""
        now = datetime.now()
        
        # Garde en cours
        active_care = PlantCare(
            plant_id=1,
            owner_id=1,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            status=CareStatus.IN_PROGRESS
        )
        
        # Garde future
        future_care = PlantCare(
            plant_id=1,
            owner_id=1,
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=8),
            status=CareStatus.ACCEPTED
        )
        
        # Garde passée
        past_care = PlantCare(
            plant_id=1,
            owner_id=1,
            start_date=now - timedelta(days=8),
            end_date=now - timedelta(days=1),
            status=CareStatus.COMPLETED
        )
        
        # Test de logique d'activité (implémentation manuelle pour le test)
        def is_care_active(care):
            return (care.start_date <= now <= care.end_date 
                   and care.status == CareStatus.IN_PROGRESS)
        
        assert is_care_active(active_care) is True
        assert is_care_active(future_care) is False
        assert is_care_active(past_care) is False
    
    def test_plant_care_with_photos(self):
        """Test d'une garde avec photos"""
        plant_care = PlantCare(
            plant_id=1,
            owner_id=1,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
            care_instructions="Plante à l'intérieur",
            start_photo_url="/photos/start.jpg",
            status=CareStatus.PENDING
        )
        
        assert plant_care.start_photo_url == "/photos/start.jpg"
    
    def test_plant_care_default_values(self):
        """Test des valeurs par défaut"""
        plant_care = PlantCare(
            plant_id=1,
            owner_id=1,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        # Les valeurs par défaut dépendent du modèle SQLAlchemy
        assert plant_care.status is None or plant_care.status == CareStatus.PENDING
        assert plant_care.caretaker_id is None
        assert plant_care.created_at is None  # Sera défini lors de l'ajout en BDD