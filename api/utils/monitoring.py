import logging
import time
from functools import wraps
from datetime import datetime
from fastapi import Request, Response
from typing import Callable, Dict, Optional
import json
import os
from pathlib import Path

# Créer le dossier logs s'il n'existe pas
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configuration du logging pour les métriques
metrics_logger = logging.getLogger("metrics")
metrics_logger.setLevel(logging.INFO)

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
    """Middleware pour monitorer les requêtes avec logging détaillé"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log et monitoring
        log_request(request, response, duration)
        monitor_response_time(request.url.path, duration)
        
        # Ajouter les headers de monitoring
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        track_error(request.url.path, e)
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