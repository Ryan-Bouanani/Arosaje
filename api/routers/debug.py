from fastapi import APIRouter
from pydantic import BaseModel
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/debug",
    tags=["debug"]
)

class LogMessage(BaseModel):
    message: str

@router.post("/log")
async def log_message(log: LogMessage):
    """Endpoint pour logger les messages de debug pendant les tests"""
    logger.info(log.message)
    return {"status": "success"} 