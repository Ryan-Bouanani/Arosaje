from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils.database import Base, engine, SessionLocal
from routers import (
    auth,
    plant,
    monitoring,
    photo,
    plant_care,
    advice,
    message,
    ws,
    admin,
    metrics,
)
from routers import care_report, botanist_report_advice, geocoding
import os
from scripts.init_data import init_data
# Import all models to ensure they're registered with Base.metadata
from models.user import User
from models.plant import Plant
from models.plant_care import PlantCare
from models.message import Message, Conversation, ConversationParticipant
from models.advice import Advice
from models.photo import Photo
from models.care_report import CareReport
from models.botanist_report_advice import BotanistReportAdvice
from models.user_status import UserStatus, UserPresence, UserTypingStatus

from utils.settings import PROJECT_NAME, VERSION
from utils.monitoring import monitoring_middleware
from services.rgpd_cleanup_service import RGPDCleanupService

app = FastAPI(title=PROJECT_NAME, version=VERSION)

# Créer les tables si elles n'existent pas
print("🔧 Création des tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès")

# Vérifier si c'est le premier lancement en cherchant l'utilisateur root
db = SessionLocal()
try:
    root_exists = (
        db.query(User).filter(User.email == "root@arosaje.fr").first() is not None
    )
    if not root_exists:
        print("🌱 Premier lancement détecté, initialisation des données...")
        init_data()
    else:
        print("ℹ️ Les données existent déjà")
finally:
    db.close()

# Configuration du CORS (doit être en premier)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend web
        "http://localhost:5001",  # Mobile app
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5001",
        "*",  # Temporaire pour debug complet
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Platform",
        "X-Client-Platform",
        "User-Agent",
        "X-Requested-With",
    ],
    expose_headers=["*"],
    max_age=3600,
)

app.middleware("http")(monitoring_middleware)


@app.middleware("http")
async def add_utf8_header(request, call_next):
    response = await call_next(request)
    # Ne modifier le Content-Type que si c'est déjà du JSON
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


# Monter le dossier static pour les images
# Utiliser le chemin absolu basé sur la racine de l'application
assets_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
if not os.path.exists(assets_directory):
    os.makedirs(assets_directory)

# Créer les sous-dossiers nécessaires
os.makedirs(os.path.join(assets_directory, "persisted_img"), exist_ok=True)
os.makedirs(os.path.join(assets_directory, "temp_img"), exist_ok=True)
os.makedirs(os.path.join(assets_directory, "img"), exist_ok=True)

# Créer le dossier uploads pour les care reports
uploads_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
if not os.path.exists(uploads_directory):
    os.makedirs(uploads_directory)
os.makedirs(os.path.join(uploads_directory, "care_reports"), exist_ok=True)

app.mount("/assets", StaticFiles(directory=assets_directory), name="assets")
app.mount("/uploads", StaticFiles(directory=uploads_directory), name="uploads")

# Inclure les routers
app.include_router(auth.router)
app.include_router(plant.router)
app.include_router(monitoring.router)
app.include_router(photo.router)
app.include_router(plant_care.router)
app.include_router(advice.router)
app.include_router(message.router)
app.include_router(ws.router)
app.include_router(admin.router)
app.include_router(metrics.router)
app.include_router(care_report.router)
app.include_router(botanist_report_advice.router)
app.include_router(geocoding.router)

# Démarrage du service RGPD
rgpd_service = RGPDCleanupService()
rgpd_service.start()


@app.get("/")
def read_root():
    return {"message": "API A'rosa-je prête !"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.options("/{path:path}")
async def options_handler():
    """Handler pour les requêtes OPTIONS (preflight CORS)"""
    return {"status": "ok"}
