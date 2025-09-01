from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from utils.database import get_db
from utils.security import get_current_user
from models.user import User, UserRole
from crud import care_report as crud_care_report
from models.care_report import CareReport as CareReportModel
from schemas.care_report import CareReport, CareReportCreate, CareReportWithDetails
import os
import uuid
from datetime import datetime

router = APIRouter(
    prefix="/care-reports",
    tags=["care-reports"]
)

@router.post("/", response_model=CareReport)
async def create_care_report(
    care_report: CareReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau rapport de séance d'entretien"""
    return crud_care_report.create_care_report(
        db=db,
        care_report=care_report,
        caretaker_id=current_user.id
    )

@router.post("/{report_id}/photo")
async def upload_care_report_photo(
    report_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add photo to a care report
    
    **Formats supportés** : JPG, JPEG, PNG, GIF
    
    **Restrictions** :
    - Seul l'auteur du rapport peut ajouter une photo
    - Le rapport doit exister
    - Une seule photo par rapport (remplace la précédente si elle existe)
    """
    # Vérifier que le rapport existe et appartient à l'utilisateur
    report = db.query(CareReportModel).filter(
        CareReportModel.id == report_id,
        CareReportModel.caretaker_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    
    # Créer le dossier uploads s'il n'existe pas
    uploads_dir = "uploads/care_reports"
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Générer un nom de fichier unique
    file_extension = photo.filename.split(".")[-1] if "." in photo.filename else ""
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(uploads_dir, filename)
    
    # Sauvegarder le fichier
    with open(file_path, "wb") as buffer:
        buffer.write(await photo.read())
    
    # Construire l'URL HTTP accessible
    photo_url = f"/uploads/care_reports/{filename}"
    
    # Mettre à jour le rapport avec l'URL de la photo
    report.photo_url = photo_url
    db.commit()
    
    return {"message": "Photo uploadée avec succès", "photo_url": photo_url}

@router.get("/plant-care/{plant_care_id}", response_model=List[CareReport])
def get_reports_by_plant_care(
    plant_care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Historique des rapports pour une garde spécifique
    
    **Tri** : Rapports triés par date de soin (plus récent en premier)
    
    **Accès** : Propriétaire de la plante, gardien, botanistes
    """
    return crud_care_report.get_care_reports_by_plant_care(db, plant_care_id)

@router.get("/my-reports", response_model=List[CareReport])
def get_my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tous mes rapports de séances d'entretien
    
    **Utilisation** : Suivi de l'activité du gardien, portfolio des soins
    
    **Tri** : Rapports triés par date de création (plus récent en premier)
    """
    return crud_care_report.get_care_reports_by_caretaker(db, current_user.id)

@router.get("/for-botanist", response_model=List[CareReportWithDetails])
def get_reports_for_botanist(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rapports nécessitant l'avis d'un botaniste
    
    **Filtrage** : Exclut les rapports déjà commentés par ce botaniste
    
    🔒 **Accès réservé aux botanistes**
    """
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(status_code=403, detail="Accès réservé aux botanistes")
    
    result = crud_care_report.get_care_reports_for_botanist(db, current_user.id, skip, limit)
    return result

@router.get("/with-my-advice", response_model=List[CareReportWithDetails])
def get_reports_with_my_advice(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rapports déjà commentés par ce botaniste
    
    **Utilisation** : Portfolio des conseils donnés, suivi des cas traités
    
    🔒 **Accès réservé aux botanistes**
    """
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(status_code=403, detail="Accès réservé aux botanistes")
    
    result = crud_care_report.get_care_reports_with_my_advice(db, current_user.id, skip, limit)
    return result

@router.get("/my-plants", response_model=List[CareReport])
def get_reports_for_my_plants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rapports des gardes de mes plantes (propriétaires)
    
    **Utilisation** :
    - Suivi des soins apportés à mes plantes
    - Vérification du travail des gardiens
    - Historique complet des interventions
    
    **Tri** : Rapports triés par date de soin (plus récent en premier)
    """
    return crud_care_report.get_care_reports_by_owner(db, current_user.id)