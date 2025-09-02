"""
Service de nettoyage RGPD - Suppression automatique des messages anciens
Conforme aux exigences: durée définie + service planifié
"""

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from utils.database import get_db
from models.message import Message
from config.rgpd import MESSAGE_RETENTION_DAYS, CLEANUP_SCHEDULE_HOUR
import logging

logger = logging.getLogger(__name__)

class RGPDCleanupService:
    """Service de nettoyage automatique conforme RGPD"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.retention_days = MESSAGE_RETENTION_DAYS
        
    def start(self):
        """Démarre le service de nettoyage planifié"""
        self.scheduler.add_job(
            func=self.cleanup_old_messages,
            trigger='cron',
            hour=CLEANUP_SCHEDULE_HOUR,
            minute=0,
            id='rgpd_message_cleanup'
        )
        self.scheduler.start()
        logger.info(f"Service RGPD démarré - Rétention: {self.retention_days} jours")
        
    def stop(self):
        """Arrête le service de nettoyage"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Service RGPD arrêté")
            
    def cleanup_old_messages(self):
        """Supprime les messages de plus de MESSAGE_RETENTION_DAYS jours"""
        db = next(get_db())
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            # Suppression des messages anciens
            deleted_count = db.query(Message).filter(
                Message.sent_at < cutoff_date
            ).delete()
            
            db.commit()
            logger.info(f"RGPD Cleanup: {deleted_count} messages supprimés (>{self.retention_days}j)")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur nettoyage RGPD: {e}")
        finally:
            db.close()
            
    def manual_cleanup(self) -> dict:
        """Nettoyage manuel pour tests/demo"""
        self.cleanup_old_messages()
        return {"status": "success", "retention_days": self.retention_days}