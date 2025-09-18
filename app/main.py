from fastapi import FastAPI
from app.controllers import food_controller, category_controller, notification_controller
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.db import Base, engine, SessionLocal
from app.entities.category import Category
from app.entities.food import Food
from datetime import date

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas automáticamente si no existen
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Food Inventory API",
    lifespan=lifespan
)

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