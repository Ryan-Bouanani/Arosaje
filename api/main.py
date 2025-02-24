from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils.database import Base, engine, SessionLocal
from routers import auth, plant, monitoring, photo, plant_care, advice, message, debug, ws, admin
from models.user import User, UserRole
from utils.password import get_password_hash
from sqlalchemy.orm import Session

from utils.settings import CORS_ALLOW_ORIGINS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS, PROJECT_NAME, VERSION
from utils.monitoring import monitoring_middleware

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION
)

def init_admin_account(db: Session):
    """Initialise ou met à jour le compte admin"""
    admin_data = {
        "email": "root@arosa.fr",
        "password": "epsi691",
        "nom": "Admin",
        "prenom": "System",
        "role": UserRole.ADMIN,
        "is_verified": True  # Le compte admin est toujours vérifié
    }

    # Vérifier si l'admin existe déjà
    admin = db.query(User).filter(User.email == admin_data["email"]).first()
    
    if admin:
        # Mettre à jour l'admin existant
        admin.password = get_password_hash(admin_data["password"])
        admin.role = admin_data["role"]
        admin.is_verified = admin_data["is_verified"]
        db.add(admin)
    else:
        # Créer un nouvel admin
        admin = User(
            email=admin_data["email"],
            password=get_password_hash(admin_data["password"]),
            nom=admin_data["nom"],
            prenom=admin_data["prenom"],
            role=admin_data["role"],
            is_verified=admin_data["is_verified"]
        )
        db.add(admin)
    
    db.commit()
    print("✅ Compte admin initialisé avec succès")

# Créer les tables
Base.metadata.create_all(bind=engine)

# Initialiser le compte admin
db = SessionLocal()
try:
    init_admin_account(db)
finally:
    db.close()

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
