from pydantic import BaseModel
from datetime import date

class CategoryCreateDTO(BaseModel):
    name: str

class CategoryResponseDTO(CategoryCreateDTO):
    id: int

    class Config:
        orm_mode = True
