from datetime import datetime, timedelta
from fastapi import HTTPException, status
from redis import RedisError
from utils.redis_client import get_redis_client

redis_client = get_redis_client()

class RateLimiter:
    @staticmethod
    def check_rate_limit(user_id: int, action: str, max_requests: int, time_window: int):
        """
        Vérifie si l'utilisateur a dépassé la limite de requêtes.
        
        Args:
            user_id: ID de l'utilisateur
            action: Type d'action (ex: 'send_message')
            max_requests: Nombre maximum de requêtes autorisées
            time_window: Fenêtre de temps en secondes
        
        Raises:
            HTTPException: Si la limite est dépassée
        """
        key = f"rate_limit:{action}:{user_id}"
        
        try:
            # Obtenir le nombre actuel de requêtes
            current = redis_client.get(key)
            
            if current is None:
                # Première requête
                redis_client.setex(key, time_window, 1)
            else:
                current = int(current)
                if current >= max_requests:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Trop de requêtes. Réessayez dans {redis_client.ttl(key)} secondes."
                    )
                
                # Incrémenter le compteur
                redis_client.incr(key)
        
        except RedisError as e:
            # Logger l'erreur mais laisser passer la requête
            print(f"Erreur Redis: {str(e)}")
            pass 