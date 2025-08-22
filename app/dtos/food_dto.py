from pydantic import BaseModel
from datetime import date
from .category_dto import CategoryResponseDTO

class FoodCreateDTO(BaseModel):
    name: str
    category_id: int
    admission_date: date

class FoodResponseDTO(BaseModel):
    id: int
    name: str
    admission_date: date
    category: CategoryResponseDTO

    class Config:
        orm_mode = True
