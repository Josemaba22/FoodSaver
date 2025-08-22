from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.db import SessionLocal
from app.services import category_service
from app.dtos.category_dto import CategoryCreateDTO, CategoryResponseDTO
from typing import List

router = APIRouter(prefix="/categories", tags=["categories"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[CategoryResponseDTO])
def get_categories(db: Session = Depends(get_db)):
    return category_service.list_categories(db)

@router.get("/{category_id}", response_model=CategoryResponseDTO)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return category_service.retrieve_category(db, category_id)

@router.post("/", response_model=CategoryResponseDTO)
def create_category(category: CategoryCreateDTO, db: Session = Depends(get_db)):
    return category_service.add_category(db, category)

@router.put("/{category_id}", response_model=CategoryResponseDTO)
def update_category(category_id: int, category: CategoryCreateDTO, db: Session = Depends(get_db)):
    return category_service.update_category(db, category_id, category)

@router.delete("/{category_id}", response_model=dict)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category_service.delete_category(db, category_id)
    return {"message": "Category deleted successfully"}
