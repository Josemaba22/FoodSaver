from pydantic import BaseModel
from datetime import date

class FoodCreateDTO(BaseModel):
    name: str
    category_id: int
    admission_date: date

class FoodResponseDTO(FoodCreateDTO):
    id: int

    class Config:
        orm_mode = True
