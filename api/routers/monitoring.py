from fastapi import APIRouter, Depends
from utils.monitoring import get_monitoring_stats
from utils.security import get_current_user

router = APIRouter(
    prefix="/monitoring",
    tags=["monitoring"],
    dependencies=[Depends(get_current_user)]  # Sécuriser l'accès aux métriques
)

@router.get("/stats")
async def get_stats():
    """Récupère les statistiques de monitoring de l'API"""
    return get_monitoring_stats() 