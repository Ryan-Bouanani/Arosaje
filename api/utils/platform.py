from enum import Enum
from fastapi import Request

class Platform(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    UNKNOWN = "unknown"

def detect_platform(request: Request) -> Platform:
    """Détecte la plateforme à partir des headers de la requête"""
    # Vérifier le header personnalisé X-Platform
    platform = request.headers.get("X-Platform")
    if platform:
        platform = platform.lower()
        if platform in [Platform.IOS, Platform.ANDROID, Platform.WEB]:
            return Platform(platform)
    
    # Vérifier le header personnalisé X-Client-Platform
    client_platform = request.headers.get("X-Client-Platform")
    if client_platform:
        client_platform = client_platform.lower()
        if "ios" in client_platform:
            return Platform.IOS
        elif "android" in client_platform:
            return Platform.ANDROID
    
    # Vérifier le User-Agent
    user_agent = request.headers.get("User-Agent", "").lower()
    
    # Détection plus précise pour les applications mobiles
    if "dart" in user_agent or "flutter" in user_agent:
        # Vérifier les marqueurs spécifiques à iOS/Android dans le User-Agent
        if any(ios_marker in user_agent for ios_marker in ["iphone", "ipad", "ipod", "ios"]):
            return Platform.IOS
        elif "android" in user_agent:
            return Platform.ANDROID
    # Détection standard pour les navigateurs web
    elif any(browser in user_agent for browser in ["mozilla", "chrome", "safari", "firefox", "edge"]):
        return Platform.WEB
    
    return Platform.UNKNOWN 