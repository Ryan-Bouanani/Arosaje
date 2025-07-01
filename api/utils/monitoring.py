import logging
import time
from functools import wraps
from datetime import datetime
from fastapi import Request, Response
from typing import Callable, Dict, Optional
import json
import os
from pathlib import Path
from services.monitoring_service import monitoring_service
from services.analytics_service import analytics_service
from utils.platform import detect_platform, Platform

# Créer le dossier logs s'il n'existe pas
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configuration du logging pour les métriques
metrics_logger = logging.getLogger("metrics")
metrics_logger.setLevel(logging.INFO)
# Empêcher la propagation des logs vers le logger parent (qui affiche dans la console)
metrics_logger.propagate = False

# Handler pour le fichier de log des métriques
metrics_file = logging.FileHandler(log_dir / "metrics.log")
metrics_file.setLevel(logging.INFO)

# Handler pour le fichier de log des erreurs
error_file = logging.FileHandler(log_dir / "errors.log")
error_file.setLevel(logging.ERROR)

# Formatter pour un format JSON structuré
class JsonFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, dict):
            return json.dumps(record.msg)
        return json.dumps({
            'message': record.msg,
            'level': record.levelname,
            'timestamp': self.formatTime(record)
        })

# Appliquer le formatter JSON
json_formatter = JsonFormatter()
metrics_file.setFormatter(json_formatter)
error_file.setFormatter(json_formatter)

# Ajouter les handlers au logger
metrics_logger.addHandler(metrics_file)
metrics_logger.addHandler(error_file)

# Stockage en mémoire des métriques
request_times: Dict[str, float] = {}
error_counts: Dict[str, int] = {}
alert_thresholds = {
    'response_time': 1.0,  # secondes
    'error_rate': 0.1,     # 10% des requêtes
    'requests_per_minute': 100
}

def log_request(request: Request, response: Response, duration: float):
    """Log les détails de la requête et la réponse dans un format structuré"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'request': {
            'method': request.method,
            'path': request.url.path,
            'query_params': str(request.query_params),
            'client_ip': request.client.host if request.client else None,
            'headers': dict(request.headers)
        },
        'response': {
            'status_code': response.status_code,
            'headers': dict(response.headers)
        },
        'performance': {
            'duration': f"{duration:.3f}s",
            'duration_ms': int(duration * 1000)
        }
    }
    metrics_logger.info(log_data)

def monitor_response_time(endpoint: str, duration: float):
    """Surveille le temps de réponse et déclenche des alertes si nécessaire"""
    request_times[endpoint] = duration
    if duration > alert_thresholds['response_time']:
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'performance_alert',
            'endpoint': endpoint,
            'duration': f"{duration:.3f}s",
            'threshold': f"{alert_thresholds['response_time']}s"
        }
        metrics_logger.warning(alert_data)

def track_error(endpoint: str, error: Exception = None):
    """Suit les erreurs par endpoint avec plus de détails"""
    error_counts[endpoint] = error_counts.get(endpoint, 0) + 1
    error_data = {
        'timestamp': datetime.now().isoformat(),
        'type': 'error',
        'endpoint': endpoint,
        'error_count': error_counts[endpoint],
        'error_message': str(error) if error else None,
        'error_type': type(error).__name__ if error else None
    }
    metrics_logger.error(error_data)

async def monitoring_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware pour monitorer les requêtes avec logging détaillé et envoi vers InfluxDB"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Détecter la plateforme
        platform = detect_platform(request)
        
        # Log et monitoring traditionnel
        log_request(request, response, duration)
        monitor_response_time(request.url.path, duration)
        
        # Envoi vers InfluxDB avec le nouveau service de monitoring
        try:
            # Récupérer l'ID utilisateur depuis les headers ou auth
            user_id = None
            if hasattr(request.state, 'user_id'):
                user_id = getattr(request.state, 'user_id')
            elif 'Authorization' in request.headers:
                # Tentative d'extraction simple - à adapter selon votre système d'auth
                pass
            
            # Envoyer toutes les métriques vers InfluxDB
            await monitoring_service.track_api_request(request, response, duration, user_id)
            
            # Tracker la fonctionnalité utilisée
            if user_id:
                # Extraire le nom de la fonctionnalité à partir du chemin
                path_parts = request.url.path.strip('/').split('/')
                if len(path_parts) > 0:
                    feature = path_parts[0]  # Utiliser la première partie du chemin comme nom de fonctionnalité
                    if len(path_parts) > 1:
                        feature += f"_{path_parts[1]}"  # Ajouter la seconde partie si elle existe
                    
                    await analytics_service.track_feature_usage(
                        feature=feature,
                        platform=platform,
                        user_id=user_id
                    )
                
                # Tracker la durée de session si c'est une requête authentifiée
                if request.url.path != "/auth/login" and request.url.path != "/auth/logout":
                    await analytics_service.track_session_duration(
                        duration_seconds=duration,
                        platform=platform,
                        user_id=user_id
                    )
                
                # Tracker la localisation si disponible
                if "x-forwarded-for" in request.headers:
                    # Note: Dans un environnement de production, il faudrait utiliser un service de géolocalisation
                    await analytics_service.track_geographic_usage(
                        country_code="FR",  # Par défaut pour le moment
                        platform=platform,
                        user_id=user_id
                    )
            
        except Exception as monitoring_error:
            # Log l'erreur de monitoring sans interrompre la requête
            metrics_logger.error({
                'timestamp': datetime.now().isoformat(),
                'type': 'monitoring_error',
                'error': str(monitoring_error),
                'endpoint': request.url.path
            })
        
        # Ajouter les headers de monitoring
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        track_error(request.url.path, e)
        
        # Envoyer l'erreur vers InfluxDB
        try:
            user_id = None
            if hasattr(request.state, 'user_id'):
                user_id = getattr(request.state, 'user_id')
                
            await monitoring_service.send_error_to_influxdb(
                error_type=type(e).__name__,
                error_message=str(e),
                endpoint=request.url.path,
                user_id=user_id,
                platform=detect_platform(request)
            )
        except Exception as monitoring_error:
            metrics_logger.error({
                'timestamp': datetime.now().isoformat(),
                'type': 'monitoring_error_during_exception',
                'error': str(monitoring_error)
            })
            
        raise

def monitor_endpoint(func):
    """Décorateur pour monitorer les endpoints spécifiques"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            monitor_response_time(func.__name__, duration)
            return result
        except Exception as e:
            track_error(func.__name__, e)
            raise
    return wrapper

def get_monitoring_stats():
    """Récupère les statistiques de monitoring avec plus de détails"""
    return {
        'timestamp': datetime.now().isoformat(),
        'metrics': {
            'request_times': {
                endpoint: f"{duration:.3f}s" 
                for endpoint, duration in request_times.items()
            },
            'error_counts': error_counts,
            'total_endpoints_monitored': len(request_times)
        },
        'thresholds': alert_thresholds
    }