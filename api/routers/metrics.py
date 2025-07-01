from fastapi import APIRouter, Response
from services.monitoring_service import monitoring_service

router = APIRouter(prefix="/metrics", tags=["monitoring"])

@router.get("")
async def get_prometheus_metrics():
    """Endpoint pour exposer les métriques Prometheus"""
    metrics_data = monitoring_service.get_prometheus_metrics()
    return Response(
        content=metrics_data,
        media_type=monitoring_service.get_metrics_content_type()
    )

@router.get("/health")
async def monitoring_health():
    """Health check pour le système de monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "monitoring": "active"
    } 