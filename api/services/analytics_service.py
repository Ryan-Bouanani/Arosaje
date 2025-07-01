from datetime import datetime, timezone
from typing import Dict, Any, Optional
from prometheus_client import Counter, Gauge, Histogram
import json
from services.monitoring_service import monitoring_service

class AnalyticsService:
    def __init__(self):
        # Métriques pour la durée des sessions
        self.session_duration = Histogram(
            'arosaje_session_duration_seconds',
            'Session duration in seconds',
            ['platform'],
            buckets=[60, 300, 900, 1800, 3600, 7200, 14400]  # 1m, 5m, 15m, 30m, 1h, 2h, 4h
        )

        # Métriques pour la distribution géographique
        self.geographic_usage = Counter(
            'arosaje_geographic_usage_total',
            'Geographic usage distribution',
            ['country_code', 'platform']
        )

    async def track_feature_usage(self, feature: str, platform: str = "unknown", user_id: Optional[str] = None):
        """Enregistre l'utilisation d'une fonctionnalité"""
        # Utiliser le compteur du service de monitoring
        monitoring_service.feature_usage.labels(feature=feature, platform=platform).inc()

        # Envoyer l'événement à InfluxDB
        await monitoring_service.send_usage_event_to_influxdb(
            event_type="feature_usage",
            user_id=user_id,
            platform=platform,
            properties={
                "feature": feature
            }
        )

    async def track_session_duration(self, duration_seconds: float, platform: str = "unknown", user_id: Optional[str] = None):
        """Enregistre la durée d'une session"""
        # Enregistrer dans Prometheus
        self.session_duration.labels(platform=platform).observe(duration_seconds)

        # Envoyer à InfluxDB
        await monitoring_service.send_usage_event_to_influxdb(
            event_type="session_end",
            user_id=user_id,
            platform=platform,
            properties={
                "duration_seconds": duration_seconds
            }
        )

    async def track_geographic_usage(self, country_code: str, platform: str = "unknown", user_id: Optional[str] = None):
        """Enregistre l'utilisation par zone géographique"""
        # Incrémenter le compteur Prometheus
        self.geographic_usage.labels(country_code=country_code, platform=platform).inc()

        # Envoyer à InfluxDB
        await monitoring_service.send_usage_event_to_influxdb(
            event_type="geographic_usage",
            user_id=user_id,
            platform=platform,
            properties={
                "country_code": country_code
            }
        )

# Instance globale du service d'analytics
analytics_service = AnalyticsService() 