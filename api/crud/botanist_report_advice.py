from sqlalchemy.orm import Session, joinedload
from typing import List
from models.botanist_report_advice import BotanistReportAdvice
from models.user import User
from schemas.botanist_report_advice import BotanistReportAdviceCreate

def create_botanist_report_advice(db: Session, advice: BotanistReportAdviceCreate, botanist_id: int) -> BotanistReportAdvice:
    """Créer un nouvel avis de botaniste sur un rapport"""
    db_advice = BotanistReportAdvice(
        care_report_id=advice.care_report_id,
        botanist_id=botanist_id,
        advice_text=advice.advice_text
    )
    db.add(db_advice)
    db.commit()
    db.refresh(db_advice)
    return db_advice

def get_botanist_advices_by_care_report(db: Session, care_report_id: int) -> List[BotanistReportAdvice]:
    """Récupérer tous les avis pour un rapport donné"""
    return db.query(BotanistReportAdvice)\
        .options(joinedload(BotanistReportAdvice.botanist))\
        .filter(BotanistReportAdvice.care_report_id == care_report_id)\
        .order_by(BotanistReportAdvice.created_at.desc())\
        .all()

def get_botanist_advices_by_botanist(db: Session, botanist_id: int) -> List[BotanistReportAdvice]:
    """Récupérer tous les avis donnés par un botaniste"""
    return db.query(BotanistReportAdvice)\
        .options(joinedload(BotanistReportAdvice.care_report))\
        .filter(BotanistReportAdvice.botanist_id == botanist_id)\
        .order_by(BotanistReportAdvice.created_at.desc())\
        .all()

def update_botanist_report_advice(db: Session, advice_id: int, advice_text: str, botanist_id: int) -> BotanistReportAdvice:
    """Mettre à jour un avis de botaniste existant"""
    db_advice = db.query(BotanistReportAdvice).filter(
        BotanistReportAdvice.id == advice_id,
        BotanistReportAdvice.botanist_id == botanist_id  # S'assurer que c'est bien son avis
    ).first()
    
    if not db_advice:
        raise ValueError("Avis non trouvé ou vous n'avez pas l'autorisation de le modifier")
    
    db_advice.advice_text = advice_text
    db.commit()
    db.refresh(db_advice)
    return db_advice

def get_my_advice_for_report(db: Session, care_report_id: int, botanist_id: int) -> BotanistReportAdvice:
    """Récupérer mon avis pour un rapport donné (s'il existe)"""
    return db.query(BotanistReportAdvice).filter(
        BotanistReportAdvice.care_report_id == care_report_id,
        BotanistReportAdvice.botanist_id == botanist_id
    ).first()

def get_care_reports_with_my_advice(db: Session, botanist_id: int):
    """Récupérer tous les rapports sur lesquels le botaniste a donné un avis"""
    from models.care_report import CareReport
    from models.plant_care import PlantCare
    from models.plant import Plant
    
    return db.query(CareReport)\
        .options(
            joinedload(CareReport.plant_care).joinedload(PlantCare.plant),
            joinedload(CareReport.caretaker),
            joinedload(CareReport.botanist_advices)
        )\
        .join(BotanistReportAdvice, CareReport.id == BotanistReportAdvice.care_report_id)\
        .filter(BotanistReportAdvice.botanist_id == botanist_id)\
        .order_by(CareReport.session_date.desc())\
        .all()