import logging
import hashlib
import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import Request, Response
import psycopg2
from psycopg2.extras import DictCursor
import aiohttp
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import os
from pathlib import Path
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from utils.platform import Platform

# Configuration pour la conformité RGPD
ANONYMIZATION_SALT = os.getenv("MONITORING_SALT", "arosaje_salt_2024")

class MonitoringService:
    def __init__(self):
        # Métriques Prometheus
        self.request_count = Counter(
            'arosaje_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status_code', 'platform']
        )
        
        self.request_duration = Histogram(
            'arosaje_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'platform']
        )
        
        self.active_users = Gauge(
            'arosaje_active_users',
            'Number of active users',
            ['platform']
        )
        
        # Initialiser le compteur d'utilisateurs actifs pour chaque plateforme
        for platform in Platform:
            self.active_users.labels(platform=platform).set(0)
        
        self.feature_usage = Counter(
            'arosaje_feature_usage_total',
            'Feature usage counter',
            ['feature', 'platform']
        )
        
        self.error_count = Counter(
            'arosaje_errors_total',
            'Total number of errors',
            ['error_type', 'endpoint', 'platform']
        )
        
        # Configuration des logs
        self._setup_logging()
        
        # Configuration base de données monitoring
        self.monitoring_db_config = {
            'host': os.getenv('MONITORING_DB_HOST', 'monitoring-postgres'),
            'port': os.getenv('MONITORING_DB_PORT', '5432'),
            'database': os.getenv('MONITORING_DB_NAME', 'monitoring_db'),
            'user': os.getenv('MONITORING_DB_USER', 'app_monitoring'),
            'password': os.getenv('MONITORING_DB_PASSWORD', 'app_monitoring_2024')
        }
        
        # Configuration InfluxDB
        self.influxdb_url = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
        self.influxdb_token = os.getenv('INFLUXDB_TOKEN', 'arosaje-token-12345678')
        self.influxdb_org = os.getenv('INFLUXDB_ORG', 'arosaje')
        self.influxdb_bucket = os.getenv('INFLUXDB_BUCKET', 'metrics')
        
        # Client InfluxDB (initialisé de manière paresseuse)
        self._influxdb_client = None
        self._write_api = None

    def _setup_logging(self):
        """Configure le logging structuré"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Logger pour les métriques business
        self.business_logger = logging.getLogger("business_metrics")
        self.business_logger.setLevel(logging.INFO)
        self.business_logger.propagate = False
        
        business_handler = logging.FileHandler(log_dir / "business_metrics.log")
        business_handler.setFormatter(self._get_json_formatter())
        self.business_logger.addHandler(business_handler)
        
        # Logger pour les erreurs
        self.error_logger = logging.getLogger("monitoring_errors")
        self.error_logger.setLevel(logging.ERROR)
        self.error_logger.propagate = False
        
        error_handler = logging.FileHandler(log_dir / "monitoring_errors.log")
        error_handler.setFormatter(self._get_json_formatter())
        self.error_logger.addHandler(error_handler)

    def _get_json_formatter(self):
        """Retourne un formatter JSON pour les logs"""
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                if isinstance(record.msg, dict):
                    return json.dumps(record.msg)
                return json.dumps({
                    'message': record.msg,
                    'level': record.levelname,
                    'timestamp': self.formatTime(record)
                })
        return JsonFormatter()

    def anonymize_user_id(self, user_id: str) -> str:
        """Anonymise l'ID utilisateur avec hash SHA-256 (conformité RGPD)"""
        if not user_id:
            return ""
        return hashlib.sha256(f"{user_id}{ANONYMIZATION_SALT}".encode()).hexdigest()

    def get_prometheus_metrics(self) -> str:
        """Retourne les métriques Prometheus au format texte"""
        return generate_latest()

    def get_metrics_content_type(self) -> str:
        """Retourne le content-type pour les métriques Prometheus"""
        return CONTENT_TYPE_LATEST

    def _get_influxdb_client(self):
        """Retourne le client InfluxDB (initialisé de manière paresseuse)"""
        if self._influxdb_client is None:
            try:
                self._influxdb_client = InfluxDBClient(
                    url=self.influxdb_url,
                    token=self.influxdb_token,
                    org=self.influxdb_org
                )
                self._write_api = self._influxdb_client.write_api(write_options=SYNCHRONOUS)
            except Exception as e:
                self.error_logger.error({
                    "error": "Failed to initialize InfluxDB client",
                    "details": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                return None
        return self._influxdb_client

    async def send_business_metric_to_influxdb(self, metric_name: str, value: float, 
                                             user_id: str = None, platform: str = "api", 
                                             tags: Dict[str, str] = None):
        """Envoie une métrique business vers InfluxDB (données anonymisées)"""
        try:
            client = self._get_influxdb_client()
            if not client or not self._write_api:
                return

            # Créer le point de données avec anonymisation
            point = Point("business_metrics") \
                .tag("platform", platform) \
                .tag("metric_name", metric_name) \
                .field("value", value) \
                .time(datetime.now(timezone.utc), WritePrecision.NS)

            # Ajouter l'utilisateur anonymisé si fourni
            if user_id:
                point = point.tag("user_hash", self.anonymize_user_id(user_id))

            # Ajouter des tags additionnels
            if tags:
                for key, value in tags.items():
                    point = point.tag(key, value)

            # Écrire vers InfluxDB
            self._write_api.write(bucket=self.influxdb_bucket, record=point)

            # Logging structuré
            self.business_logger.info({
                "metric_name": metric_name,
                "value": value,
                "platform": platform,
                "user_hash": self.anonymize_user_id(user_id) if user_id else None,
                "tags": tags,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        except Exception as e:
            self.error_logger.error({
                "error": "Failed to send business metric to InfluxDB",
                "metric_name": metric_name,
                "details": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    async def send_performance_metric_to_influxdb(self, metric_type: str, value_ms: int,
                                                endpoint: str = None, user_id: str = None,
                                                platform: str = "api", tags: Dict[str, str] = None):
        """Envoie une métrique de performance vers InfluxDB"""
        try:
            client = self._get_influxdb_client()
            if not client or not self._write_api:
                return

            point = Point("performance_metrics") \
                .tag("platform", platform) \
                .tag("metric_type", metric_type) \
                .field("value_ms", value_ms) \
                .time(datetime.now(timezone.utc), WritePrecision.NS)

            if endpoint:
                point = point.tag("endpoint", endpoint)

            if user_id:
                point = point.tag("user_hash", self.anonymize_user_id(user_id))

            if tags:
                for key, value in tags.items():
                    point = point.tag(key, value)

            self._write_api.write(bucket=self.influxdb_bucket, record=point)

        except Exception as e:
            self.error_logger.error({
                "error": "Failed to send performance metric to InfluxDB",
                "metric_type": metric_type,
                "details": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    async def send_usage_event_to_influxdb(self, event_type: str, user_id: str = None,
                                         platform: str = Platform.WEB, properties: Dict[str, Any] = None):
        """Envoie un événement d'utilisation vers InfluxDB"""
        try:
            client = self._get_influxdb_client()
            if not client or not self._write_api:
                return

            # Créer le point de données
            point = Point("usage_events") \
                .tag("event_type", event_type) \
                .tag("platform", platform) \
                .time(datetime.now(timezone.utc), WritePrecision.NS)

            # Ajouter l'utilisateur anonymisé si fourni
            if user_id:
                point = point.tag("user_hash", self.anonymize_user_id(user_id))

            # Ajouter les propriétés comme champs
            if properties:
                for key, value in properties.items():
                    if isinstance(value, (int, float)):
                        point = point.field(key, value)
                    else:
                        point = point.field(key, str(value))

            # Écrire vers InfluxDB
            self._write_api.write(bucket=self.influxdb_bucket, record=point)

            # Logging structuré
            self.business_logger.info({
                "event_type": event_type,
                "platform": platform,
                "user_hash": self.anonymize_user_id(user_id) if user_id else None,
                "properties": properties,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        except Exception as e:
            self.error_logger.error({
                "error": "Failed to send usage event to InfluxDB",
                "event_type": event_type,
                "details": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    async def send_error_to_influxdb(self, error_type: str, error_message: str,
                                   endpoint: str = None, user_id: str = None,
                                   platform: str = Platform.WEB, stack_trace: str = None):
        """Envoie une erreur vers InfluxDB"""
        try:
            client = self._get_influxdb_client()
            if not client or not self._write_api:
                return

            # Créer le point de données
            point = Point("errors") \
                .tag("error_type", error_type) \
                .tag("platform", platform)

            if endpoint:
                point = point.tag("endpoint", endpoint)

            if user_id:
                point = point.tag("user_hash", self.anonymize_user_id(user_id))

            point = point.field("error_message", error_message)

            if stack_trace:
                point = point.field("stack_trace", stack_trace)

            point = point.time(datetime.now(timezone.utc), WritePrecision.NS)

            # Écrire vers InfluxDB
            self._write_api.write(bucket=self.influxdb_bucket, record=point)

            # Incrémenter le compteur Prometheus
            self.error_count.labels(
                error_type=error_type,
                endpoint=endpoint or "unknown",
                platform=platform
            ).inc()

            # Logging structuré
            self.error_logger.error({
                "error_type": error_type,
                "error_message": error_message,
                "endpoint": endpoint,
                "platform": platform,
                "user_hash": self.anonymize_user_id(user_id) if user_id else None,
                "stack_trace": stack_trace,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        except Exception as e:
            self.error_logger.error({
                "error": "Failed to send error to InfluxDB",
                "error_type": error_type,
                "details": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    async def track_api_request(self, request: Request, response: Response, 
                              response_time: float, user_id: str = None):
        """Track une requête API avec toutes les métriques associées"""
        from utils.platform import detect_platform
        
        # Détecter la plateforme
        platform = detect_platform(request)
        
        # Incrémenter le compteur de requêtes
        self.request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            platform=platform
        ).inc()
        
        # Observer le temps de réponse
        self.request_duration.labels(
            method=request.method,
            endpoint=request.url.path,
            platform=platform
        ).observe(response_time)
        
        # Envoyer les métriques vers InfluxDB
        await self.send_performance_metric_to_influxdb(
            metric_type="response_time",
            value_ms=int(response_time * 1000),
            endpoint=request.url.path,
            user_id=user_id,
            platform=platform,
            tags={
                "method": request.method,
                "status_code": str(response.status_code)
            }
        )

    def decrement_active_users(self, platform: str = Platform.WEB):
        """Décrémente le compteur d'utilisateurs actifs"""
        current = self.active_users.labels(platform=platform)._value.get()
        if current > 0:  # Éviter les valeurs négatives
            self.active_users.labels(platform=platform).dec()

    def increment_active_users(self, platform: str = Platform.WEB):
        """Incrémente le compteur d'utilisateurs actifs"""
        self.active_users.labels(platform=platform).inc()

    def close(self):
        """Ferme les connexions InfluxDB"""
        if self._influxdb_client:
            self._influxdb_client.close()

# Instance globale du service de monitoring
monitoring_service = MonitoringService() 