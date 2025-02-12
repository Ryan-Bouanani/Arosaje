from redis import Redis
from utils.settings import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_USERNAME, REDIS_PASSWORD

# Connexion à Redis avec les paramètres de configuration
redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def get_redis_client() -> Redis:
    """Retourne une instance du client Redis"""
    return redis_client 