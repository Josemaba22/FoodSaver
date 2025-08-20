from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.db import SessionLocal
from app.services import food_service
from app.dtos.food_dto import FoodCreateDTO, FoodResponseDTO
from typing import List

router = APIRouter(prefix="/foods", tags=["foods"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[FoodResponseDTO])
def get_foods(db: Session = Depends(get_db)):
    return food_service.list_foods(db)

@router.get("/{food_id}", response_model=FoodResponseDTO)
def get_food(food_id: int, db: Session = Depends(get_db)):
    return food_service.retrieve_food(db, food_id)

@router.post("/", response_model=FoodResponseDTO)
def create_food(food: FoodCreateDTO, db: Session = Depends(get_db)):
    return food_service.add_food(db, food) 
    
