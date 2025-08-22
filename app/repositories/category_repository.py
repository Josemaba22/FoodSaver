from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.entities.category import Category
from app.dtos.category_dto import CategoryCreateDTO

def get_categories(db: Session):
    return db.query(Category).all()

def get_category_by_id(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

def create_category(db: Session, category_dto: CategoryCreateDTO):
    category = Category(**category_dto.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def update_category(db: Session, category_id: int, category_dto: CategoryCreateDTO):
    category = get_category_by_id(db, category_id)
    for key, value in category_dto.dict().items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category

def delete_category(db: Session, category_id: int):
    category = get_category_by_id(db, category_id)
    db.delete(category)
    db.commit()