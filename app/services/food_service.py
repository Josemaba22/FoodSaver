from sqlalchemy.orm import Session
from app.repositories import food_repository
from app.dtos.food_dto import FoodCreateDTO
import httpx

def list_foods(db: Session, page: int = 1, size: int = 10, sort: str = None):
    return food_repository.get_foods(db, page, size, sort)

# Nueva función para obtener todos los alimentos sin paginación
def list_all_foods(db: Session):
    return food_repository.get_all_foods(db)

def retrieve_food(db: Session, food_id: int):
    return food_repository.get_food_by_id(db, food_id)

def add_food(db: Session, food_dto: FoodCreateDTO):
    return food_repository.create_food(db, food_dto)

def update_food(db: Session, food_id: int, food_dto: FoodCreateDTO):
    return food_repository.update_food(db, food_id, food_dto)

def delete_food(db: Session, food_id: int):
    food_repository.delete_food(db, food_id)

async def get_recipe_from_mcp():
    mcp_url = "http://<MCP_HOST>:<MCP_PORT>/food/all"  # Cambia por la URL real del MCP
    async with httpx.AsyncClient() as client:
        response = await client.get(mcp_url)
        response.raise_for_status()
        return response.json()