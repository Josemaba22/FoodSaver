from fastapi import APIRouter, Depends, Query, File, UploadFile
from sqlalchemy.orm import Session
from app.config.db import SessionLocal
from app.services import food_service
from app.dtos.food_dto import FoodCreateDTO, FoodResponseDTO
from typing import List, Optional
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import io
from PIL import Image
import os
import shutil
from fastapi import HTTPException

router = APIRouter(prefix="/foods", tags=["foods"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/all", response_model=List[FoodResponseDTO])
def get_all_foods(db: Session = Depends(get_db)):
    return food_service.list_all_foods(db)

@router.get("/")
def get_foods(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort: Optional[str] = Query(None, description="Sort field (e.g., name.asc or admission_date.desc)"),
    db: Session = Depends(get_db)
):
    return food_service.list_foods(db, page, size, sort)

@router.get("/{food_id}", response_model=FoodResponseDTO)
def get_food(food_id: int, db: Session = Depends(get_db)):
    return food_service.retrieve_food(db, food_id)

@router.post("/", response_model=FoodResponseDTO)
def create_food(food: FoodCreateDTO, db: Session = Depends(get_db)):
    return food_service.add_food(db, food)

@router.put("/{food_id}", response_model=FoodResponseDTO)
def update_food(food_id: int, food: FoodCreateDTO, db: Session = Depends(get_db)):
    return food_service.update_food(db, food_id, food)

@router.delete("/{food_id}", response_model=dict)
def delete_food(food_id: int, db: Session = Depends(get_db)):
    food_service.delete_food(db, food_id)
    return {"message": "Food deleted successfully"}

# Cargar el modelo una sola vez al iniciar el servidor
try:
    MODEL_PATH = "app/foodimage/modelo_pizza_steak.h5"
    model = load_model(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Error cargando el modelo: {e}")

@router.post("/predict-image/")
async def predict_image(file: UploadFile = File(...)):
    # Ruta donde se guardará la imagen (raíz del proyecto)
    save_path = os.path.join(os.getcwd(), file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Simulación de predicción
    pred_class = 1  # Simulado
    pred_score = 0.99  # Simulado
    class_names = {1: "pizza", 2: "carne"}
    class_name = class_names.get(pred_class, "desconocido")

    return {
        "predicted_class": pred_class,
        "class_name": class_name,
        "score": pred_score,
        "saved_path": save_path
    }


@router.get("/recipe/")
async def get_recipe():
    try:
        recipe = await food_service.get_recipe_from_mcp()
        return recipe
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error comunicando con MCP: {str(e)}")