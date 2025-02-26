from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils.database import Base, engine
from routers import auth, plant, monitoring, photo, plant_care, advice, message, debug, ws, admin
from scripts.init_data import init_data
import os

from utils.settings import CORS_ALLOW_ORIGINS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS, PROJECT_NAME, VERSION
from utils.monitoring import monitoring_middleware

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION
)

# Créer les tables
Base.metadata.create_all(bind=engine)

# Initialiser les données de base
init_data()

# Middleware de monitoring
app.middleware("http")(monitoring_middleware)

# Configuration du CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
    expose_headers=["*"],
    max_age=3600,
)

# Monter le dossier static pour les images
# Utiliser le chemin absolu basé sur la racine de l'application
assets_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
if not os.path.exists(assets_directory):
    os.makedirs(assets_directory)

# Créer les sous-dossiers nécessaires
os.makedirs(os.path.join(assets_directory, "persisted_img"), exist_ok=True)
os.makedirs(os.path.join(assets_directory, "temp_img"), exist_ok=True)
os.makedirs(os.path.join(assets_directory, "img"), exist_ok=True)

app.mount("/assets", StaticFiles(directory=assets_directory), name="assets")

# Inclure les routers
app.include_router(auth.router)
app.include_router(plant.router)
app.include_router(monitoring.router)
app.include_router(photo.router)
app.include_router(plant_care.router)
app.include_router(advice.router)
app.include_router(message.router)
app.include_router(debug.router)
app.include_router(ws.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "API A'rosa-je prête !"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
