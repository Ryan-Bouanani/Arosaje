from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, not_, exists
from typing import List, Optional
from models.care_report import CareReport
from models.botanist_report_advice import BotanistReportAdvice
from models.user import User, UserRole
from models.plant_care import PlantCare
from models.plant import Plant
from schemas.care_report import CareReportCreate, CareReportWithDetails
from datetime import datetime

def create_care_report(db: Session, care_report: CareReportCreate, caretaker_id: int, photo_url: Optional[str] = None) -> CareReport:
    """Créer un nouveau rapport de séance d'entretien"""
    db_report = CareReport(
        plant_care_id=care_report.plant_care_id,
        caretaker_id=caretaker_id,
        health_level=care_report.health_level,
        hydration_level=care_report.hydration_level,
        vitality_level=care_report.vitality_level,
        description=care_report.description,
        photo_url=photo_url
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_care_reports_by_plant_care(db: Session, plant_care_id: int) -> List[CareReport]:
    """Récupérer tous les rapports pour une garde donnée avec les avis botanistes"""
    return db.query(CareReport)\
        .options(joinedload(CareReport.botanist_advices).joinedload(BotanistReportAdvice.botanist))\
        .filter(CareReport.plant_care_id == plant_care_id)\
        .order_by(CareReport.session_date.desc())\
        .all()

def get_care_reports_by_caretaker(db: Session, caretaker_id: int) -> List[CareReport]:
    """Récupérer tous les rapports créés par un gardien"""
    return db.query(CareReport).filter(CareReport.caretaker_id == caretaker_id).order_by(CareReport.session_date.desc()).all()

def get_care_reports_for_botanist(db: Session, botanist_id: int, skip: int = 0, limit: int = 100) -> List[CareReport]:
    """Récupérer tous les rapports sans avis du botaniste actuel"""
    # Filtrer les rapports qui n'ont pas encore d'avis du botaniste connecté
    return db.query(CareReport)\
        .options(
            joinedload(CareReport.plant_care).joinedload(PlantCare.plant),
            joinedload(CareReport.caretaker)
        )\
        .filter(
            not_(exists().where(
                and_(
                    BotanistReportAdvice.care_report_id == CareReport.id,
                    BotanistReportAdvice.botanist_id == botanist_id
                )
            ))
        )\
        .order_by(CareReport.session_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_care_reports_with_my_advice(db: Session, botanist_id: int, skip: int = 0, limit: int = 100) -> List[CareReport]:
    """Récupérer tous les rapports avec avis du botaniste actuel"""
    return db.query(CareReport)\
        .options(
            joinedload(CareReport.plant_care).joinedload(PlantCare.plant),
            joinedload(CareReport.caretaker),
            joinedload(CareReport.botanist_advices)
        )\
        .filter(
            exists().where(
                and_(
                    BotanistReportAdvice.care_report_id == CareReport.id,
                    BotanistReportAdvice.botanist_id == botanist_id
                )
            )
        )\
        .order_by(CareReport.session_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_care_reports_by_owner(db: Session, owner_id: int) -> List[CareReport]:
    """Récupérer tous les rapports des plantes d'un propriétaire"""
    return db.query(CareReport).join(
        PlantCare, CareReport.plant_care_id == PlantCare.id
    ).filter(
        PlantCare.owner_id == owner_id
    ).order_by(
        CareReport.session_date.desc()
    ).all()