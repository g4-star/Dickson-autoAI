from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database.db import Base, engine

from app.models import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dickson's autoAI API",
    description="Backend API for Dickson's autonomous AI job assistant.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "Dickson's autoAI",
        "status": "running",
        "version": "0.1.0",
    }