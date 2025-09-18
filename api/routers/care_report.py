from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from typing import List
import base64
from utils.database import get_db
from utils.security import get_current_user
from models.user import User, UserRole
from crud import care_report as crud_care_report
from models.care_report import CareReport as CareReportModel
from schemas.care_report import CareReport, CareReportCreate, CareReportWithDetails

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

    # Valider et encoder l'image en Base64
    try:
        # Validation de base - Flutter Web peut envoyer content_type=null
        print(f"DEBUG: Received file - name: {photo.filename}, content_type: {photo.content_type}")

        # Accepter les images même si content_type est manquant (Flutter Web issue)
        if photo.content_type and not photo.content_type.startswith("image/") and photo.content_type != "application/octet-stream":
            raise HTTPException(status_code=400, detail="Le fichier doit être une image")
        
        # Lire le contenu de l'image
        await photo.seek(0)
        image_data = await photo.read()
        
        # Vérifier la taille (max 5MB pour éviter des problèmes de DB)
        if len(image_data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="L'image ne peut pas dépasser 5MB")
        
        # Encoder en Base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Créer le data URL avec le type MIME (défaut si manquant)
        mime_type = photo.content_type or "image/jpeg"
        if mime_type == "application/octet-stream":
            mime_type = "image/jpeg"  # Flutter Web fallback
        data_url = f"data:{mime_type};base64,{base64_image}"
        
        print(f"DEBUG: Photo encoded successfully - Content-Type: {photo.content_type}, Size: {len(image_data)} bytes")

    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Photo encoding failed - Error: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Erreur lors de l'upload: {str(e)}"
        )

    # Mettre à jour le rapport avec l'image Base64
    report.photo_base64 = data_url
    # Conserver l'ancien champ pour compatibilité (optionnel)
    report.photo_url = None
    db.commit()

    return {"message": "Photo uploadée avec succès", "photo_base64": True}


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


@router.get("/{report_id}/image")
def get_care_report_image(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Servir l'image d'un rapport de garde en format binaire pour contourner
    les problèmes de décodage base64 dans Flutter Web"""

    # Récupérer le rapport
    report = db.query(CareReportModel).filter(CareReportModel.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")

    if not report.photo_base64:
        raise HTTPException(status_code=404, detail="Aucune image trouvée pour ce rapport")

    try:
        # Extraire le type MIME et les données base64
        if report.photo_base64.startswith('data:'):
            # Format: data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...
            header, base64_data = report.photo_base64.split(',', 1)
            mime_type = header.split(':')[1].split(';')[0]
        else:
            # Si c'est juste du base64 sans préfixe
            base64_data = report.photo_base64
            mime_type = "image/jpeg"  # Défaut

        # Décoder les données base64
        image_bytes = base64.b64decode(base64_data)

        # Retourner l'image en tant que réponse binaire
        return Response(
            content=image_bytes,
            media_type=mime_type,
            headers={
                "Cache-Control": "max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de l'image: {str(e)}")
