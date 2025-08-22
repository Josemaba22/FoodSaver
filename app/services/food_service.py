from sqlalchemy.orm import Session
from app.repositories import food_repository
from app.dtos.food_dto import FoodCreateDTO

def list_foods(db: Session):
    return food_repository.get_foods(db)

def retrieve_food(db: Session, food_id: int):
    return food_repository.get_food_by_id(db, food_id)

def add_food(db: Session, food_dto: FoodCreateDTO):
    return food_repository.create_food(db, food_dto)

def update_food(db: Session, food_id: int, food_dto: FoodCreateDTO):
    return food_repository.update_food(db, food_id, food_dto)

def delete_food(db: Session, food_id: int):
    food_repository.delete_food(db, food_id)
