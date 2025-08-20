from sqlalchemy.orm import Session
from app.entities.food import Food
from app.entities.category import Category
from datetime import date, timedelta

import pdb

def get_expiring_foods(db: Session, days_before_expiry: int = 2):
    today = date.today()
    upcoming_date = today + timedelta(days=days_before_expiry)

    # Aquí suponemos que cada alimento dura 7 días (ejemplo).  
    # En el futuro podrías tener una tabla con "shelf_life_days" por categoría.
    shelf_life_days = 7  

    results = db.query(Food, Category).join(Category).all()

    notifications = []
    for food, category in results:
        expiry_date = food.admission_date + timedelta(days=shelf_life_days)
        notifications.append({
            "food_id": food.id,
            "user_id": 1,  # en MVP usuario único
            "message": f"⚠️ Tu {food.name} ({category.name}) caduca el {expiry_date}"
        })
        if today <= expiry_date <= upcoming_date:
            notifications.append({
                "food_id": food.id,
                "user_id": 1,  # en MVP usuario único
                "message": f"⚠️ Tu {food.name} ({category.name}) caduca el {expiry_date}"
            })
    return notifications
