from pydantic import BaseModel
from datetime import date
from typing import Optional
from .category_dto import CategoryResponseDTO

class FoodCreateDTO(BaseModel):
    name: str
    category_id: int
    admission_date: date
    image_url: Optional[str] = None  # Campo opcional para la URL de la imagen

class FoodResponseDTO(BaseModel):
    id: int
    name: str
    admission_date: date
    image_url: Optional[str] = None  # URL de la imagen
    category: CategoryResponseDTO

    class Config:
        orm_mode = True
