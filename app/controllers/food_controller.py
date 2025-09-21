from fastapi import APIRouter, Depends, Query, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from app.config.db import SessionLocal
from app.services import food_service
from app.dtos.food_dto import FoodCreateDTO, FoodResponseDTO
from app.utils.image_handler import save_image, delete_image
from app.entities.food import Food
from typing import List, Optional
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import io
from PIL import Image
import os
import shutil
from datetime import date

router = APIRouter(prefix="/foods", tags=["foods"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/all", response_model=List[FoodResponseDTO])
def get_all_foods(db: Session = Depends(get_db)):
    return food_service.list_all_foods(db)

@router.get("/")
def get_foods(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort: Optional[str] = Query(None, description="Sort field (e.g., name.asc or admission_date.desc)"),
    db: Session = Depends(get_db)
):
    return food_service.list_foods(db, page, size, sort)

@router.get("/{food_id}", response_model=FoodResponseDTO)
def get_food(food_id: int, db: Session = Depends(get_db)):
    return food_service.retrieve_food(db, food_id)

@router.post("/", response_model=FoodResponseDTO)
def create_food(food: FoodCreateDTO, db: Session = Depends(get_db)):
    return food_service.add_food(db, food)

@router.post("/with-image/", response_model=FoodResponseDTO)
async def create_food_with_image(
    name: str = Form(...),
    category_id: int = Form(...),
    admission_date: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Crear una comida con imagen
    
    Args:
        name: Nombre de la comida
        category_id: ID de la categoría
        admission_date: Fecha de admisión (formato: YYYY-MM-DD)
        image: Archivo de imagen
        db: Sesión de base de datos
    
    Returns:
        Información de la comida creada con la URL de la imagen
    """
    image_url = None
    try:
        # Guardar la imagen
        image_url = await save_image(image)
        
        # Parsear la fecha
        parsed_date = date.fromisoformat(admission_date)
        
        # Crear el registro de comida
        food_data = Food(
            name=name,
            category_id=category_id,
            admission_date=parsed_date,
            image_url=image_url
        )
        
        db.add(food_data)
        db.commit()
        db.refresh(food_data)
        
        return food_data
        
    except ValueError as e:
        # Error de fecha
        if image_url:
            delete_image(image_url)
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {str(e)}")
        
    except Exception as e:
        # Limpiar imagen si hay error
        if image_url:
            delete_image(image_url)
        raise HTTPException(status_code=500, detail=f"Error creando comida: {str(e)}")

@router.put("/{food_id}", response_model=FoodResponseDTO)
def update_food(food_id: int, food: FoodCreateDTO, db: Session = Depends(get_db)):
    return food_service.update_food(db, food_id, food)

@router.delete("/{food_id}", response_model=dict)
def delete_food(food_id: int, db: Session = Depends(get_db)):
    food_service.delete_food(db, food_id)
    return {"message": "Food deleted successfully"}

# Cargar el modelo una sola vez al iniciar el servidor
try:
    MODEL_PATH = "foodimage/modelo_frutas.h5"
    model = load_model(MODEL_PATH)
    print("✅ Modelo de frutas cargado exitosamente")
except Exception as e:
    model = None
    print(f"❌ Error cargando el modelo: {e}")

# Clases del modelo (en español)
class_indices_es = {
    'manzana': 0, 'banana': 1, 'remolacha': 2, 'pimiento': 3, 'repollo': 4,
    'pimiento_rojo': 5, 'zanahoria': 6, 'coliflor': 7, 'chile': 8, 'maiz': 9,
    'pepino': 10, 'berenjena': 11, 'ajo': 12, 'jengibre': 13, 'uvas': 14,
    'jalapeno': 15, 'kiwi': 16, 'limon': 17, 'lechuga': 18, 'mango': 19,
    'cebolla': 20, 'naranja': 21, 'paprika': 22, 'pera': 23, 'guisantes': 24,
    'pina': 25, 'granada': 26, 'papa': 27, 'rabano': 28,
    'soja': 29, 'espinaca': 30, 'maiz_dulce': 31, 'camote': 32,
    'tomate': 33, 'nabo': 34, 'sandia': 35
}

# Crear diccionario inverso para convertir índice → nombre de clase
idx_to_class_es = {v: k for k, v in class_indices_es.items()}

@router.post("/predict-image/")
async def predict_image(
    file: UploadFile = File(...),
    save_to_database: bool = Form(False),
    category_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Predice el tipo de fruta/vegetal en una imagen usando el modelo entrenado.
    Opcionalmente guarda la imagen y crea un registro en la base de datos.
    
    Args:
        file: Imagen a analizar
        save_to_database: Si True, guarda el registro en la BD
        category_id: ID de categoría (requerido si save_to_database=True)
        db: Sesión de base de datos
    
    Returns:
        Predicción del modelo y opcionalmente información del registro creado
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no disponible")
    
    # Verificar que el archivo sea una imagen
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    # Si se va a guardar en BD, validar que se proporcione category_id
    if save_to_database and category_id is None:
        raise HTTPException(
            status_code=400, 
            detail="category_id es requerido cuando save_to_database=True"
        )
    
    image_url = None
    try:
        # 1. GUARDAR LA IMAGEN FÍSICAMENTE
        image_url = await save_image(file)
        
        # 2. PROCESAR LA IMAGEN PARA PREDICCIÓN
        # Leer la imagen desde el archivo guardado
        # Extraer el path físico desde la URL
        image_filename = image_url.split("/")[-1]
        image_path = f"uploads/images/{image_filename}"
        
        # Cargar y procesar la imagen para el modelo
        img = Image.open(image_path)
        
        # Convertir a RGB si es necesario
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar la imagen a 224x224 (tamaño esperado por el modelo)
        img = img.resize((224, 224))
        
        # Convertir a array numpy y normalizar
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Añadir dimensión batch
        img_array = img_array.astype('float32') / 255.0  # Normalizar
        
        # 3. HACER LA PREDICCIÓN
        predictions = model.predict(img_array)[0]
        
        # Obtener la clase con mayor probabilidad
        predicted_class_idx = np.argmax(predictions)
        confidence = float(predictions[predicted_class_idx])
        
        # Convertir índice a nombre de clase
        predicted_class_name = idx_to_class_es.get(predicted_class_idx, "desconocido")
        
        # Obtener las top 3 predicciones
        top_3_indices = np.argsort(predictions)[-3:][::-1]
        top_3_predictions = [
            {
                "class_name": idx_to_class_es.get(idx, "desconocido"),
                "confidence": float(predictions[idx])
            }
            for idx in top_3_indices
        ]
        
        # 4. PREPARAR RESPUESTA BASE
        response = {
            "success": True,
            "predicted_class": int(predicted_class_idx),
            "class_name": predicted_class_name,
            "confidence": confidence,
            "top_3_predictions": top_3_predictions,
            "filename": file.filename,
            "image_url": image_url,
            "image_saved": True
        }
        
        # 5. GUARDAR EN BASE DE DATOS SI SE SOLICITA
        if save_to_database:
            try:
                # Crear registro de Food con la imagen
                food_data = Food(
                    name=predicted_class_name.title(),  # Capitalizar el nombre
                    category_id=category_id,
                    admission_date=date.today(),
                    image_url=image_url
                )
                
                db.add(food_data)
                db.commit()
                db.refresh(food_data)
                
                # Añadir información del registro creado a la respuesta
                response.update({
                    "database_saved": True,
                    "food_record": {
                        "id": food_data.id,
                        "name": food_data.name,
                        "category_id": food_data.category_id,
                        "admission_date": food_data.admission_date.isoformat(),
                        "image_url": food_data.image_url
                    }
                })
                
            except Exception as db_error:
                # Si falla la BD, eliminar la imagen guardada
                delete_image(image_url)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error guardando en base de datos: {str(db_error)}"
                )
        else:
            response["database_saved"] = False
        
        return response
        
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        if image_url:
            delete_image(image_url)
        raise
        
    except Exception as e:
        # Para cualquier otro error, limpiar la imagen si se guardó
        if image_url:
            delete_image(image_url)
        raise HTTPException(status_code=500, detail=f"Error procesando la imagen: {str(e)}")
    
    finally:
        # Cerrar el archivo si está abierto
        if hasattr(file, 'file'):
            file.file.close()


@router.get("/recipe/")
async def get_recipe():
    try:
        recipe = await food_service.get_recipe_from_mcp()
        return recipe
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error comunicando con MCP: {str(e)}")