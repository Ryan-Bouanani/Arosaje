from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils.database import Base, engine
from routers import auth, plant, monitoring, photo, plant_care
from utils.settings import CORS_ALLOW_ORIGINS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS, PROJECT_NAME, VERSION
from utils.monitoring import monitoring_middleware

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION
)

# Créer les tables
Base.metadata.create_all(bind=engine)

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
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Inclure les routers
app.include_router(auth.router)
app.include_router(plant.router)
app.include_router(monitoring.router)
app.include_router(photo.router)
app.include_router(plant_care.router)

@app.get("/")
def read_root():
    return {"message": "API A'rosa-je prête !"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
