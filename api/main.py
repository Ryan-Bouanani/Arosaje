from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.database import Base, engine
from routers import user_router
from utils.settings import CORS_ORIGINS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS

app = FastAPI()

# Créer les tables
Base.metadata.create_all(bind=engine)


# Inclure les routers
app.include_router(user_router.router)

# Configuration du CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

@app.get("/")
def read_root():
    return {"message": "API A'rosa-je prête !"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
