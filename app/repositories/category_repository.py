from sqlalchemy.orm import Session
from app.entities.category import Category
from app.dtos.category_dto import CategoryCreateDTO

def get_categories(db: Session):
    return db.query(Category).all()

def get_category_by_id(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()

def create_category(db: Session, category_dto: CategoryCreateDTO):
    db_category = Category(**category_dto.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category
