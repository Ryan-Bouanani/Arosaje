from fastapi import APIRouter, Depends
from utils.monitoring import get_monitoring_stats
from utils.security import get_current_user

router = APIRouter(
    prefix="/monitoring", tags=["monitoring"], dependencies=[Depends(get_current_user)]
)


@router.get("/stats")
async def get_stats():
    """Statistiques de monitoring de l'API"""
    return get_monitoring_stats()
