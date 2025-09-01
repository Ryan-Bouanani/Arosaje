import os
import logging
import aiohttp
from typing import Optional, Tuple
from dotenv import load_dotenv
import json

load_dotenv()

logger = logging.getLogger(__name__)

class GoogleGeocodingService:
    """Service pour géocoder les adresses en utilisant l'API Google Geocoding"""
    
    def __init__(self):
        # IMPORTANT: Remplacer par une nouvelle clé avec restrictions appropriées
        self.api_key = os.getenv("GOOGLE_GEOCODING_API_KEY", "AIzaSyDGGp6USx0kYrG1DtIE6g7_UKmz7p4ARcM")
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Géocode une adresse et retourne les coordonnées (latitude, longitude)
        
        Args:
            address: L'adresse à géocoder
            
        Returns:
            Tuple[float, float]: (latitude, longitude) ou None si échec
        """
        if not address or not address.strip():
            logger.warning("Adresse vide fournie pour le géocodage")
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "address": address,
                    "key": self.api_key,
                    "region": "fr",  # Privilégier les résultats en France
                    "language": "fr"  # Résultats en français
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Erreur API Google Geocoding: {response.status}")
                        return None
                        
                    data = await response.json()
                    
                    if data.get("status") != "OK":
                        logger.warning(f"Géocodage échoué pour '{address}': {data.get('status')}")
                        
                        # Si aucun résultat, essayer avec une version simplifiée
                        if data.get("status") == "ZERO_RESULTS" and "," in address:
                            # Essayer avec juste la ville
                            city = address.split(",")[-1].strip()
                            logger.info(f"Tentative avec la ville seulement: {city}")
                            return await self._geocode_fallback(city)
                        return None
                    
                    # Extraire les coordonnées du premier résultat
                    results = data.get("results", [])
                    if not results:
                        logger.warning(f"Aucun résultat pour l'adresse: {address}")
                        return None
                        
                    location = results[0]["geometry"]["location"]
                    lat = location["lat"]
                    lng = location["lng"]
                    
                    # Log l'adresse formatée pour débogage
                    formatted_address = results[0].get("formatted_address", address)
                    logger.info(f"Géocodage réussi: '{formatted_address}' -> ({lat}, {lng})")
                    
                    return (lat, lng)
                    
        except Exception as e:
            logger.error(f"Erreur lors du géocodage de '{address}': {str(e)}")
            return None
    
    async def _geocode_fallback(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Géocodage de secours pour une localisation simplifiée
        """
        # Coordonnées par défaut pour quelques villes majeures
        default_coords = {
            "paris": (48.8566, 2.3522),
            "lyon": (45.764043, 4.835659),
            "marseille": (43.296482, 5.36978),
            "toulouse": (43.604652, 1.444209),
            "nice": (43.710173, 7.261953),
            "nantes": (47.218371, -1.553621),
            "strasbourg": (48.573405, 7.752111),
            "montpellier": (43.610769, 3.876716),
            "bordeaux": (44.837789, -0.57918),
            "lille": (50.62925, 3.057256)
        }
        
        location_lower = location.lower().strip()
        
        # Chercher dans les coordonnées par défaut
        for city, coords in default_coords.items():
            if city in location_lower:
                logger.info(f"Utilisation des coordonnées par défaut pour {city}")
                return coords
                
        # Si c'est un code postal parisien
        if location_lower.startswith("75"):
            logger.info("Code postal parisien détecté, utilisation des coordonnées de Paris")
            return (48.8566, 2.3522)
            
        # Sinon essayer de géocoder quand même
        return await self.geocode_address(location)

# Instance singleton
geocoding_service = GoogleGeocodingService()