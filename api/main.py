from fastapi import FastAPI
from database import Base, engine
from models import user, plant, advice, garde, photo_history

app = FastAPI()

# Créer les tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "API A'rosa-je prête !"}
