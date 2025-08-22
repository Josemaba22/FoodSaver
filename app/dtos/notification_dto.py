from pydantic import BaseModel
from datetime import date

class NotificationDTO(BaseModel):
    id: int
    user_id: int
    food_id: int
    message: str
    created_at: date

    class Config:
        orm_mode = True
