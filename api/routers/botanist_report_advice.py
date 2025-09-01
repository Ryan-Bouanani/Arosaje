from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from utils.database import get_db
from utils.security import get_current_user
from models.user import User, UserRole
from models.care_report import CareReport as CareReportModel
from crud import botanist_report_advice as crud_advice
from schemas.botanist_report_advice import (
    BotanistReportAdviceCreate, 
    BotanistReportAdviceUpdate,
    BotanistReportAdvice,
    BotanistReportAdviceWithDetails
)
from schemas.care_report import CareReportWithDetails

router = APIRouter(
    prefix="/botanist-report-advice",
    tags=["botanist-report-advice"]
)

@router.post("/", response_model=BotanistReportAdvice)
async def create_botanist_advice_on_report(
    advice: BotanistReportAdviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer un avis de botaniste sur un rapport de séance
    
    🔒 **Accès réservé aux botanistes**
    """
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(status_code=403, detail="Accès réservé aux botanistes")
    
    # Vérifier que le rapport existe
    report = db.query(CareReportModel).filter(CareReportModel.id == advice.care_report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    
    return crud_advice.create_botanist_report_advice(
        db=db,
        advice=advice,
        botanist_id=current_user.id
    )

@router.get("/care-report/{care_report_id}", response_model=List[BotanistReportAdviceWithDetails])
def get_advices_for_care_report(
    care_report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tous les avis botaniques pour un rapport spécifique
    """
    return crud_advice.get_botanist_advices_by_care_report(db, care_report_id)

@router.put("/{advice_id}", response_model=BotanistReportAdvice)
async def update_botanist_advice(
    advice_id: int,
    advice_update: BotanistReportAdviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Modifier un avis de botaniste existant
    
    **Restriction** : Seul l'auteur de l'avis peut le modifier
    
    🔒 **Accès réservé aux botanistes**
    """
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(status_code=403, detail="Accès réservé aux botanistes")
    
    try:
        return crud_advice.update_botanist_report_advice(
            db=db,
            advice_id=advice_id,
            advice_text=advice_update.advice_text,
            botanist_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/my-advised-reports", response_model=List[CareReportWithDetails])
def get_my_advised_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rapports sur lesquels j'ai donné un avis (portfolio botaniste)
    
    **Utilisation** : Portfolio des interventions, suivi des conseils donnés
    
    🔒 **Accès réservé aux botanistes**
    """
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(status_code=403, detail="Accès réservé aux botanistes")
    
    return crud_advice.get_care_reports_with_my_advice(db, current_user.id)