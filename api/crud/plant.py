from typing import Optional, List
from sqlalchemy.orm import Session
from models.plant import Plant
from schemas.plant import PlantCreate, PlantUpdate
from .base import CRUDBase

class CRUDPlant(CRUDBase[Plant, PlantCreate, PlantUpdate]):
    def get_by_owner(
        self, 
        db: Session, 
        *, 
        owner_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Plant]:
        """Méthode spécifique pour récupérer les plantes d'un propriétaire"""
        return (
            db.query(self.model)
            .filter(Plant.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

# Créer une instance pour l'utiliser dans les routes
plant = CRUDPlant(Plant) 