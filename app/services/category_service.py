from sqlalchemy.orm import Session
from app.repositories import category_repository
from app.dtos.category_dto import CategoryCreateDTO

def list_categories(db: Session):
    return category_repository.get_categories(db)

def retrieve_category(db: Session, category_id: int):
    return category_repository.get_category_by_id(db, category_id)

def add_category(db: Session, category_dto: CategoryCreateDTO):
    return category_repository.create_category(db, category_dto)

def update_category(db: Session, category_id: int, category_dto: CategoryCreateDTO):
    return category_repository.update_category(db, category_id, category_dto)

def delete_category(db: Session, category_id: int):
    category_repository.delete_category(db, category_id)
