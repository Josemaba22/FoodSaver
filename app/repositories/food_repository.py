from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.entities.food import Food
from app.dtos.food_dto import FoodCreateDTO

def get_foods(db: Session):
    return db.query(Food).all()

def get_food_by_id(db: Session, food_id: int):
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food

def create_food(db: Session, food_dto: FoodCreateDTO):
    food = Food(**food_dto.dict())
    db.add(food)
    db.commit()
    db.refresh(food)
    return food

def update_food(db: Session, food_id: int, food_dto: FoodCreateDTO):
    food = get_food_by_id(db, food_id)
    for key, value in food_dto.dict().items():
        setattr(food, key, value)
    db.commit()
    db.refresh(food)
    return food

def delete_food(db: Session, food_id: int):
    food = get_food_by_id(db, food_id)
    db.delete(food)
    db.commit()