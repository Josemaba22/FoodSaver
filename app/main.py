from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.controllers import food_controller, category_controller, notification_controller
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.db import Base, engine, SessionLocal
from app.entities.category import Category
from app.entities.food import Food
from datetime import date
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear directorio de uploads si no existe
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs("uploads/images", exist_ok=True)
    
    # Crear tablas automáticamente si no existen
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Food Inventory API",
    lifespan=lifespan
)

# Configurar para servir archivos estáticos (imágenes)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(food_controller.router)
app.include_router(category_controller.router)
app.include_router(notification_controller.router)