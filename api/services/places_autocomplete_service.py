import os
import logging
import aiohttp
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class GooglePlacesAutocompleteService:
    """Service pour l'autocomplétion d'adresses avec l'API Google Places"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_GEOCODING_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

    async def autocomplete_addresses(
        self, query: str, country_code: str = "fr"
    ) -> List[Dict]:
        """
        Récupère les suggestions d'adresses depuis l'API Google Places

        Args:
            query: Texte de recherche
            country_code: Code pays pour restreindre les résultats (fr par défaut)

        Returns:
            Liste des suggestions d'adresses
        """
        if not query or len(query.strip()) < 1:
            return []

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "input": query.strip(),
                    "key": self.api_key,
                    "language": "fr",  # Résultats en français
                    "components": f"country:{country_code}",  # Restreindre au pays
                    "types": "address",  # Filtrer sur les adresses
                }

                logger.info(f"Recherche d'adresses pour: '{query}'")

                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Erreur API Google Places: {response.status}")
                        return []

                    data = await response.json()

                    if data.get("status") != "OK":
                        logger.warning(
                            f"Autocomplétion échouée: {data.get('status')} - {data.get('error_message', '')}"
                        )
                        return []

                    # Transformer les résultats au format attendu par le frontend
                    suggestions = []
                    for prediction in data.get("predictions", []):
                        suggestion = {
                            "description": prediction.get("description", ""),
                            "place_id": prediction.get("place_id", ""),
                            "main_text": prediction.get(
                                "structured_formatting", {}
                            ).get("main_text", ""),
                            "secondary_text": prediction.get(
                                "structured_formatting", {}
                            ).get("secondary_text", ""),
                        }
                        suggestions.append(suggestion)

                    logger.info(f"Trouvé {len(suggestions)} suggestions pour '{query}'")
                    return suggestions

        except Exception as e:
            logger.error(f"Erreur lors de l'autocomplétion pour '{query}': {str(e)}")
            return []


# Instance singleton
places_autocomplete_service = GooglePlacesAutocompleteService()
