from sqlalchemy.orm import Session
from app.entities.food import Food
from app.dtos.food_dto import FoodCreateDTO

def get_foods(db: Session):
    return db.query(Food).all()

def get_food_by_id(db: Session, food_id: int):
    return db.query(Food).filter(Food.id == food_id).first()

def create_food(db: Session, food_dto: FoodCreateDTO):
    db_food = Food(**food_dto.dict())
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food
