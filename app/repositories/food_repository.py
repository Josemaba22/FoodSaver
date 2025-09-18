from sqlalchemy.orm import Session
from fastapi import HTTPException, Query
from typing import Optional
from app.entities.food import Food
from app.dtos.food_dto import FoodCreateDTO
from app.dtos.page_dto import PageResponse

def get_foods(
    db: Session,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort: Optional[str] = Query(None, description="Sort field (e.g., name.asc or name.desc)")
) -> PageResponse:
    query = db.query(Food).join(Food.category)
    
    # Aplicar ordenamiento si se especifica
    if sort:
        field, order = sort.split('.')
        if order == 'desc':
            query = query.order_by(getattr(Food, field).desc())
        else:
            query = query.order_by(getattr(Food, field).asc())
    
    # Contar total de registros
    total = query.count()
    
    # Aplicar paginación
    items = query.offset((page - 1) * size).limit(size).all()
    
    return PageResponse(
        items=items,
        page=page,
        size=size,
        total=total
    )

def get_food_by_id(db: Session, food_id: int):
    food = db.query(Food).join(Food.category).filter(Food.id == food_id).first()
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

def get_all_foods(db: Session):
    return db.query(Food).join(Food.category).all()