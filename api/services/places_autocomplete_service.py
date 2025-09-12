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

    def _get_fallback_suggestions(self, query: str) -> List[Dict]:
        """
        Retourne des suggestions d'adresses prédéfinies pour la démo
        """
        # Adresses de démonstration en France
        demo_addresses = [
            {
                "description": "123 Rue de Rivoli, 75001 Paris, France",
                "place_id": "demo_paris_1",
                "main_text": "123 Rue de Rivoli",
                "secondary_text": "75001 Paris, France"
            },
            {
                "description": "45 Avenue des Champs-Élysées, 75008 Paris, France", 
                "place_id": "demo_paris_2",
                "main_text": "45 Avenue des Champs-Élysées",
                "secondary_text": "75008 Paris, France"
            },
            {
                "description": "10 Place de la République, 69003 Lyon, France",
                "place_id": "demo_lyon_1", 
                "main_text": "10 Place de la République",
                "secondary_text": "69003 Lyon, France"
            },
            {
                "description": "25 Rue du Vieux Port, 13001 Marseille, France",
                "place_id": "demo_marseille_1",
                "main_text": "25 Rue du Vieux Port", 
                "secondary_text": "13001 Marseille, France"
            },
            {
                "description": "78 Boulevard de la Liberté, 59000 Lille, France",
                "place_id": "demo_lille_1",
                "main_text": "78 Boulevard de la Liberté",
                "secondary_text": "59000 Lille, France"
            },
            {
                "description": "15 Rue Sainte-Catherine, 33000 Bordeaux, France",
                "place_id": "demo_bordeaux_1",
                "main_text": "15 Rue Sainte-Catherine",
                "secondary_text": "33000 Bordeaux, France"
            }
        ]
        
        # Filtrer les adresses qui contiennent la requête
        query_lower = query.lower().strip()
        if len(query_lower) < 1:
            return demo_addresses[:3]  # Retourner les 3 premières si pas de requête
            
        filtered = []
        for addr in demo_addresses:
            if query_lower in addr["description"].lower() or query_lower in addr["main_text"].lower():
                filtered.append(addr)
        
        # Si aucun match exact, retourner des suggestions basées sur les mots communs
        if not filtered:
            for addr in demo_addresses:
                words = query_lower.split()
                if any(word in addr["description"].lower() for word in words if len(word) > 2):
                    filtered.append(addr)
        
        return filtered[:5]  # Limiter à 5 résultats

    async def autocomplete_addresses(
        self, query: str, country_code: str = "fr"
    ) -> List[Dict]:
        """
        Récupère les suggestions d'adresses depuis l'API Google Places ou fallback

        Args:
            query: Texte de recherche
            country_code: Code pays pour restreindre les résultats (fr par défaut)

        Returns:
            Liste des suggestions d'adresses
        """
        if not query or len(query.strip()) < 1:
            return []

        # Si pas de clé API Google, utiliser le fallback
        if not self.api_key:
            logger.info(f"Pas de clé Google API - utilisation du fallback pour: '{query}'")
            return self._get_fallback_suggestions(query)

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
                        return self._get_fallback_suggestions(query)

                    data = await response.json()

                    if data.get("status") != "OK":
                        logger.warning(
                            f"Autocomplétion échouée: {data.get('status')} - {data.get('error_message', '')} - utilisation du fallback"
                        )
                        return self._get_fallback_suggestions(query)

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
            logger.error(f"Erreur lors de l'autocomplétion pour '{query}': {str(e)} - utilisation du fallback")
            return self._get_fallback_suggestions(query)


# Instance singleton
places_autocomplete_service = GooglePlacesAutocompleteService()
