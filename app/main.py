from fastapi import FastAPI
from app.controllers import food_controller, category_controller, notification_controller

app = FastAPI(title="Food Inventory API")

app.include_router(food_controller.router)
app.include_router(category_controller.router)
app.include_router(notification_controller.router)

