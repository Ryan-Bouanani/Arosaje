from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from utils.database import Base

class BotanistReportAdvice(Base):
    __tablename__ = "botanist_report_advices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    care_report_id = Column(Integer, ForeignKey("care_reports.id", ondelete="CASCADE"), nullable=False)
    botanist_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Contenu de l'avis
    advice_text = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    care_report = relationship("CareReport", back_populates="botanist_advices")
    botanist = relationship("User", foreign_keys=[botanist_id])