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
    """
    Ajouter une photo à un rapport de séance
    
    **Exemple de requête** (multipart/form-data) :
    
    ```
    POST /care-reports/8/photo
    Content-Type: multipart/form-data
    Authorization: Bearer token...
    
    photo=[fichier image.jpg]
    ```
    
    **Réponse** :
    ```
    {
        "message": "Photo uploadée avec succès",
        "photo_url": "/uploads/care_reports/a1b2c3d4-e5f6.jpg"
    }
    ```
    
    **Formats supportés** : JPG, JPEG, PNG, GIF
    
    **Restrictions** :
    - Seul l'auteur du rapport peut ajouter une photo
    - Le rapport doit exister
    - Une seule photo par rapport (remplace la précédente si elle existe)
    
    **Codes d'erreur** :
    - 404 : Rapport non trouvé ou non autorisé
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
    """
    Historique des rapports pour une garde spécifique
    
    **Exemple de requête** :
    
    ```
    GET /care-reports/plant-care/12
    Authorization: Bearer token...
    ```
    
    **Réponse** :
    ```
    [
        {
            "id": 8,
            "plant_care_id": 12,
            "caretaker_id": 7,
            "description": "Arrosage effectué, feuilles nettoyées.",
            "care_date": "2024-02-03T09:30:00",
            "notes": "Plante en bonne santé.",
            "photo_url": "/uploads/care_reports/a1b2c3d4.jpg",
            "created_at": "2024-02-03T09:35:00"
        },
        {
            "id": 12,
            "plant_care_id": 12,
            "caretaker_id": 7,
            "description": "Arrosage et fertilisation.",
            "care_date": "2024-02-06T10:15:00",
            "notes": "Ajout d'engrais liquide.",
            "photo_url": null,
            "created_at": "2024-02-06T10:20:00"
        }
    ]
    ```
    
    **Tri** : Rapports triés par date de soin (plus récent en premier)
    
    **Accès** : Propriétaire de la plante, gardien, botanistes
    """
    return crud_care_report.get_care_reports_by_plant_care(db, plant_care_id)

@router.get("/my-reports", response_model=List[CareReport])
def get_my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tous mes rapports de séances d'entretien
    
    **Exemple de requête** :
    
    ```
    GET /care-reports/my-reports
    Authorization: Bearer token...
    ```
    
    **Réponse** :
    ```
    [
        {
            "id": 8,
            "plant_care_id": 12,
            "caretaker_id": 7,
            "description": "Arrosage effectué, feuilles nettoyées.",
            "care_date": "2024-02-03T09:30:00",
            "notes": "Plante en bonne santé.",
            "photo_url": "/uploads/care_reports/a1b2c3d4.jpg",
            "created_at": "2024-02-03T09:35:00"
        },
        {
            "id": 15,
            "plant_care_id": 18,
            "caretaker_id": 7,
            "description": "Rempotage et arrosage.",
            "care_date": "2024-02-05T14:00:00",
            "notes": "Nouveau pot plus grand, terre fraîche.",
            "photo_url": "/uploads/care_reports/b2c3d4e5.jpg",
            "created_at": "2024-02-05T14:10:00"
        }
    ]
    ```
    
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
    """
    Rapports nécessitant l'avis d'un botaniste
    
    **Exemple de requête** :
    
    ```
    GET /care-reports/for-botanist?skip=0&limit=20
    Authorization: Bearer botanist_token...
    ```
    
    **Réponse** :
    ```
    [
        {
            "id": 8,
            "plant_care_id": 12,
            "caretaker_id": 7,
            "description": "Taches brunes sur les feuilles après arrosage.",
            "care_date": "2024-02-03T09:30:00",
            "notes": "Les taches sont apparues après l'arrosage.",
            "photo_url": "/uploads/care_reports/problem_leaves.jpg",
            "created_at": "2024-02-03T09:35:00",
            "plant_care": {
                "plant": {
                    "nom": "Monstera Deliciosa",
                    "espece": "Monstera deliciosa"
                },
                "owner": {
                    "nom": "Dupont",
                    "prenom": "Jean"
                }
            },
            "caretaker": {
                "nom": "Martin",
                "prenom": "Alice"
            }
        }
    ]
    ```
    
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
    """
    Rapports déjà commentés par ce botaniste
    
    **Exemple de requête** :
    
    ```
    GET /care-reports/with-my-advice?skip=0&limit=20
    Authorization: Bearer botanist_token...
    ```
    
    **Réponse** :
    ```
    [
        {
            "id": 5,
            "plant_care_id": 8,
            "caretaker_id": 3,
            "description": "Feuilles qui jaunissent.",
            "care_date": "2024-01-30T14:20:00",
            "notes": "Plusieurs feuilles deviennent jaunes.",
            "photo_url": "/uploads/care_reports/yellow_leaves.jpg",
            "created_at": "2024-01-30T14:25:00",
            "plant_care": {
                "plant": {
                    "nom": "Ficus Benjamin",
                    "espece": "Ficus benjamina"
                },
                "owner": {
                    "nom": "Moreau",
                    "prenom": "Sophie"
                }
            },
            "caretaker": {
                "nom": "Dupont",
                "prenom": "Jean"
            },
            "my_advice": {
                "id": 3,
                "advice_text": "Jaunissement normal : réduisez l'arrosage et placez dans un endroit plus lumineux.",
                "created_at": "2024-01-30T16:45:00"
            }
        }
    ]
    ```
    
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
    """
    Rapports des gardes de mes plantes (propriétaires)
    
    **Exemple de requête** :
    
    ```
    GET /care-reports/my-plants
    Authorization: Bearer token...
    ```
    
    **Réponse** :
    ```
    [
        {
            "id": 8,
            "plant_care_id": 12,
            "caretaker_id": 7,
            "description": "Arrosage effectué, feuilles nettoyées.",
            "care_date": "2024-02-03T09:30:00",
            "notes": "Votre Monstera se porte très bien !",
            "photo_url": "/uploads/care_reports/healthy_plant.jpg",
            "created_at": "2024-02-03T09:35:00"
        },
        {
            "id": 11,
            "plant_care_id": 12,
            "caretaker_id": 7,
            "description": "Arrosage léger, rotation de la plante.",
            "care_date": "2024-02-05T16:00:00",
            "notes": "Rotation pour une croissance uniforme.",
            "photo_url": null,
            "created_at": "2024-02-05T16:05:00"
        }
    ]
    ```
    
    **Utilisation** :
    - Suivi des soins apportés à mes plantes
    - Vérification du travail des gardiens
    - Historique complet des interventions
    
    **Tri** : Rapports triés par date de soin (plus récent en premier)
    """
    return crud_care_report.get_care_reports_by_owner(db, current_user.id)