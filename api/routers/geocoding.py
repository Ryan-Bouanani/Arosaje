from typing import List
from fastapi import APIRouter, HTTPException, Query
from services.places_autocomplete_service import places_autocomplete_service
from services.geocoding_service import geocoding_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/geocoding",
    tags=["geocoding"]
)

@router.get("/autocomplete")
async def autocomplete_addresses(
    query: str = Query(..., min_length=1, description="Texte de recherche pour l'autocomplétion"),
    country: str = Query("fr", description="Code pays (fr par défaut)")
):
    """Autocomplétion d'adresses via l'API Google Places"""
    try:
        logger.info(f"Demande d'autocomplétion pour: '{query}'")
        
        suggestions = await places_autocomplete_service.autocomplete_addresses(
            query=query,
            country_code=country
        )
        
        return {
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Erreur dans l'endpoint d'autocomplétion: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors de la recherche d'adresses"
        )

@router.post("/geocode")
async def geocode_address(address: str):
    """Géocoder une adresse pour obtenir ses coordonnées"""
    try:
        logger.info(f"Demande de géocodage pour: '{address}'")
        
        coordinates = await geocoding_service.geocode_address(address)
        
        if coordinates is None:
            return {
                "address": address,
                "success": False,
                "message": "Impossible de géocoder cette adresse"
            }
        
        return {
            "address": address,
            "success": True,
            "latitude": coordinates[0],
            "longitude": coordinates[1]
        }
        
    except Exception as e:
        logger.error(f"Erreur dans l'endpoint de géocodage: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors du géocodage de l'adresse"
        )