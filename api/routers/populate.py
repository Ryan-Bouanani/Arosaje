#!/usr/bin/env python3
"""
Endpoint temporaire pour population de la production
À supprimer après utilisation
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.database import get_db
import subprocess
import os

router = APIRouter(prefix="/populate", tags=["populate"])

@router.post("/production")
async def populate_production(db: Session = Depends(get_db)):
    """
    Endpoint temporaire pour peupler la production
    ATTENTION: À supprimer après utilisation !
    """
    try:
        # Vérifier que nous sommes en production
        if os.getenv("DEBUG", "False").lower() == "true":
            raise HTTPException(status_code=403, detail="Endpoint non disponible en développement")

        # Exécuter le script de population
        result = subprocess.run(
            ["python", "/app/create_production_users.py"],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            return {
                "success": True,
                "message": "Population production terminée",
                "output": result.stdout,
                "accounts_created": [
                    "root@arosaje.fr / epsi691",
                    "user@arosaje.fr / epsi691",
                    "gardien@arosaje.fr / epsi691",
                    "botanist@arosaje.fr / epsi691",
                    "botanist2@arosaje.fr / epsi691"
                ]
            }
        else:
            return {
                "success": False,
                "message": "Erreur lors de la population",
                "error": result.stderr,
                "output": result.stdout
            }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout lors de l'exécution du script")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.get("/status")
async def get_populate_status():
    """Vérifier si l'endpoint de population est disponible"""
    return {
        "available": True,
        "message": "Endpoint de population disponible",
        "warning": "Endpoint temporaire - à supprimer après utilisation"
    }