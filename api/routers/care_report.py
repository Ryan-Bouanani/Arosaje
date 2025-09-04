from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from utils.database import get_db
from utils.security import get_current_user
from utils.image_handler import ImageHandler
from models.user import User, UserRole
from crud import care_report as crud_care_report
from models.care_report import CareReport as CareReportModel
from schemas.care_report import CareReport, CareReportCreate, CareReportWithDetails
import os
import uuid

router = APIRouter(prefix="/care-reports", tags=["care-reports"])


@router.post("/", response_model=CareReport)
async def create_care_report(
    care_report: CareReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Créer un nouveau rapport de séance d'entretien"""
    return crud_care_report.create_care_report(
        db=db, care_report=care_report, caretaker_id=current_user.id
    )


@router.post("/{report_id}/photo")
async def upload_care_report_photo(
    report_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add photo to a care report

    **Formats supportés** : JPG, JPEG, PNG, GIF

    **Restrictions** :
    - Seul l'auteur du rapport peut ajouter une photo
    - Le rapport doit exister
    - Une seule photo par rapport (remplace la précédente si elle existe)
    """
    # Vérifier que le rapport existe et appartient à l'utilisateur
    report = (
        db.query(CareReportModel)
        .filter(
            CareReportModel.id == report_id,
            CareReportModel.caretaker_id == current_user.id,
        )
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")

    # Utiliser ImageHandler pour une validation et sauvegarde sécurisées
    try:
        photo_size = getattr(photo, 'size', 'Unknown')
        print(f"DEBUG: Upload photo - Filename: {photo.filename}, Content-Type: {photo.content_type}, Size: {photo_size}")
        
        # Debug: Lire les premiers bytes pour vérifier la signature
        await photo.seek(0)  # Reset position
        first_bytes = await photo.read(16)
        await photo.seek(0)  # Reset position pour save_image
        print(f"DEBUG: First 16 bytes: {first_bytes}")
        print(f"DEBUG: First 16 bytes hex: {first_bytes.hex()}")
        
        filename, url = await ImageHandler.save_image(photo, "persisted_care_report")
        
        # Construire l'URL pour care reports (format spécifique)
        photo_url = f"/assets/persisted_img/{filename}"
        print(f"DEBUG: Photo upload successful - URL: {photo_url}")
        
    except Exception as e:
        print(f"DEBUG: Photo upload failed - Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'upload: {str(e)}")

    # Mettre à jour le rapport avec l'URL de la photo
    report.photo_url = photo_url
    db.commit()

    return {"message": "Photo uploadée avec succès", "photo_url": photo_url}


@router.get("/plant-care/{plant_care_id}", response_model=List[CareReport])
def get_reports_by_plant_care(
    plant_care_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Historique des rapports pour une garde spécifique

    **Tri** : Rapports triés par date de soin (plus récent en premier)

    **Accès** : Propriétaire de la plante, gardien, botanistes
    """
    return crud_care_report.get_care_reports_by_plant_care(db, plant_care_id)


@router.get("/my-reports", response_model=List[CareReport])
def get_my_reports(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user),
):
    """Rapports nécessitant l'avis d'un botaniste

    **Filtrage** : Exclut les rapports déjà commentés par ce botaniste

    🔒 **Accès réservé aux botanistes**
    """
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(status_code=403, detail="Accès réservé aux botanistes")

    result = crud_care_report.get_care_reports_for_botanist(
        db, current_user.id, skip, limit
    )
    return result


@router.get("/with-my-advice", response_model=List[CareReportWithDetails])
def get_reports_with_my_advice(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rapports déjà commentés par ce botaniste

    **Utilisation** : Portfolio des conseils donnés, suivi des cas traités

    🔒 **Accès réservé aux botanistes**
    """
    if current_user.role != UserRole.BOTANIST:
        raise HTTPException(status_code=403, detail="Accès réservé aux botanistes")

    result = crud_care_report.get_care_reports_with_my_advice(
        db, current_user.id, skip, limit
    )
    return result


@router.get("/my-plants", response_model=List[CareReport])
def get_reports_for_my_plants(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Rapports des gardes de mes plantes (propriétaires)

    **Utilisation** :
    - Suivi des soins apportés à mes plantes
    - Vérification du travail des gardiens
    - Historique complet des interventions

    **Tri** : Rapports triés par date de soin (plus récent en premier)
    """
    return crud_care_report.get_care_reports_by_owner(db, current_user.id)
