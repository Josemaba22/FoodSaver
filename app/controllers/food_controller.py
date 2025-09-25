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
    return {"message": "Se eliminó exitosamente"}

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


@router.post("/recipes/", response_model=dict)
async def get_recipes_by_ingredients(
    ingredients: List[str] = Form(..., description="Lista de ingredientes separados por comas"),
    db: Session = Depends(get_db)
):
    """
    Obtener recetas basadas en ingredientes usando servicio externo
    
    Args:
        ingredients: Lista de ingredientes para buscar recetas
        db: Sesión de base de datos
    
    Returns:
        JSON con ingredientes enviados y recetas obtenidas del servicio externo
    """
    import httpx
    
    try:
        # Preparar payload para el servicio externo
        payload = {
            "ingredients": ingredients
        }
        
        # Realizar petición al servicio externo de recetas
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8001/api/v1/recipes",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Verificar si la respuesta fue exitosa
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Error del servicio de recetas: HTTP {response.status_code}"
                )
            
            # Obtener respuesta del servicio
            recipes_data = response.json()
            
            # Retornar en el formato esperado
            return {
                "ingredients": ingredients,
                "recipes": recipes_data.get("recipes", [])
            }
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar al servicio de recetas. Asegúrate de que esté ejecutándose en http://localhost:8001"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Timeout al conectar con el servicio de recetas"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener recetas: {str(e)}"
        )

@router.get("/recipes/from-foods/", response_model=dict)
async def get_recipes_from_database_foods(
    db: Session = Depends(get_db)
):
    """
    Obtener recetas basadas en todos los alimentos de la base de datos
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        JSON con ingredientes extraídos de la BD y recetas del servicio externo
    """
    import httpx
    
    try:
        # Obtener todos los alimentos de la base de datos usando food_service
        foods = food_service.list_all_foods(db)
        
        if not foods:
            raise HTTPException(status_code=404, detail="No se encontraron alimentos en la base de datos")
        
        # Extraer nombres de alimentos como ingredientes
        ingredients = []
        for food in foods:
            # Convertir nombre a ingrediente (lowercase, singular básico)
            ingredient = food.name.lower().strip()
            
            # Mapeo básico para convertir a inglés (opcional)
            spanish_to_english = {
                "manzana": "apple",
                "banana": "banana", 
                "tomate": "tomato",
                "cebolla": "onion",
                "zanahoria": "carrot",
                "papa": "potato",
                "pollo": "chicken",
                "arroz": "rice",
                "ajo": "garlic",
                "pimiento": "bell pepper"
            }
            
            # Usar traducción si existe, sino usar el nombre original
            ingredient = spanish_to_english.get(ingredient, ingredient)
            
            if ingredient not in ingredients:
                ingredients.append(ingredient)
        
        # Si no hay ingredientes, error
        if not ingredients:
            raise HTTPException(status_code=400, detail="No se pudieron extraer ingredientes válidos")
        
        # Preparar payload para el servicio externo
        payload = {
            "ingredients": ingredients
        }
        
        # Realizar petición al servicio externo de recetas
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8001/api/v1/recipes",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Error del servicio de recetas: HTTP {response.status_code}"
                )
            
            recipes_data = response.json()
            
            return {
                "ingredients": ingredients,
                "recipes": recipes_data.get("recipes", []),
                "source_foods": [{"id": food.id, "name": food.name} for food in foods]
            }
            
    except HTTPException:
        raise
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar al servicio de recetas en http://localhost:8001"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar alimentos: {str(e)}"
        )

# ===== ENDPOINTS DE ALERTAS AUTOMÁTICAS =====

@router.get("/alerts/status/", response_model=dict)
def get_alerts_status():
    """
    Obtener estado del sistema de alertas automáticas
    
    Returns:
        Estado de configuración y servicios de notificaciones
    """
    from app.services.auto_notification_service import get_notification_status
    
    try:
        status = get_notification_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado de alertas: {str(e)}"
        )

@router.get("/alerts/check/", response_model=dict)
def check_foods_expiry(
    days_ahead: int = Query(3, description="Días de anticipación para verificar"),
    db: Session = Depends(get_db)
):
    """
    Verificar qué alimentos están próximos a vencer (sin enviar email)
    
    Args:
        days_ahead: Días de anticipación para la verificación
        db: Sesión de base de datos
    
    Returns:
        Lista de alimentos próximos a vencer
    """
    from app.services.auto_notification_service import get_foods_near_expiry
    
    try:
        foods_near_expiry = get_foods_near_expiry(db, days_ahead)
        
        return {
            "success": True,
            "foods_near_expiry": [
                {
                    "id": food.id,
                    "name": food.name,
                    "admission_date": food.admission_date.isoformat(),
                    "days_until_expiry": (food.admission_date - date.today()).days,
                    "category": food.category.name if hasattr(food, 'category') and food.category else None,
                    "image_url": food.image_url
                }
                for food in foods_near_expiry
            ],
            "total_count": len(foods_near_expiry),
            "check_date": date.today().isoformat(),
            "days_ahead": days_ahead
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error verificando alimentos: {str(e)}"
        )

@router.post("/alerts/send-manual/", response_model=dict)
async def send_manual_alert(
    recipient_email: str = Form(..., description="Email donde enviar la alerta"),
    days_ahead: int = Form(3, description="Días de anticipación para la alerta"),
    db: Session = Depends(get_db)
):
    """
    Enviar alerta manual por email sobre alimentos próximos a vencer
    
    Args:
        recipient_email: Email destinatario
        days_ahead: Días de anticipación (default: 3)
        db: Sesión de base de datos
    
    Returns:
        Resultado del envío del email
    """
    from app.services.auto_notification_service import get_foods_near_expiry, send_expiration_alert
    
    try:
        # Obtener alimentos próximos a vencer
        foods_near_expiry = get_foods_near_expiry(db, days_ahead)
        
        if not foods_near_expiry:
            return {
                "success": True,
                "message": "No hay alimentos próximos a vencer",
                "foods_count": 0,
                "recipient": recipient_email
            }
        
        # Enviar email
        result = await send_expiration_alert(foods_near_expiry, recipient_email)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando alerta manual: {str(e)}"
        )

@router.post("/alerts/send-auto/", response_model=dict)
async def trigger_auto_alert(db: Session = Depends(get_db)):
    """
    Disparar manualmente el proceso de alerta automática
    (útil para testing o ejecución manual del proceso automático)
    
    Returns:
        Resultado del envío automático
    """
    from app.services.auto_notification_service import auto_send_daily_alert
    
    try:
        result = await auto_send_daily_alert()
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en proceso de alerta automática: {str(e)}"
        )

@router.get("/alerts/scheduler-status/", response_model=dict)
def get_scheduler_status():
    """
    Obtener estado del scheduler de alertas automáticas
    
    Returns:
        Estado del scheduler y configuración
    """
    try:
        from app.services.scheduler_service import get_scheduler_status
        
        status = get_scheduler_status()
        return {
            "success": True,
            "scheduler": status
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "Scheduler no disponible (dependencias no instaladas)",
            "scheduler": {"running": False, "enabled": False}
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado del scheduler: {str(e)}"
        )

@router.post("/alerts/test-scheduler/", response_model=dict)
async def test_scheduler():
    """
    Probar el funcionamiento del scheduler manualmente
    
    Returns:
        Resultado de la prueba del scheduler
    """
    try:
        from app.services.scheduler_service import test_scheduler as run_test
        
        result = await run_test()
        return result
        
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Scheduler no disponible (dependencias no instaladas)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error probando scheduler: {str(e)}"
        )

@router.post("/alerts/test-jose/", response_model=dict)
async def test_email_for_jose():
    """
    Endpoint de prueba específico para verificar el envío de emails a José
    
    Returns:
        Resultado del envío del email de prueba
    """
    import resend
    from datetime import date
    
    try:
        # Email de prueba específico para José
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": ["josemaba22@gmail.com"],
            "subject": "🧪 Test Email - Food Inventory para José",
            "html": f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ color: #2E8B57; border-bottom: 2px solid #2E8B57; padding-bottom: 10px; }}
                        .success {{ background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>✅ ¡Hola José!</h1>
                    </div>
                    
                    <div class="success">
                        <p>🎉 <strong>¡Excelente noticia!</strong></p>
                        <p>Si estás leyendo este email, significa que tu sistema de alertas de Food Inventory está funcionando perfectamente.</p>
                    </div>
                    
                    <h3>📋 Información del sistema:</h3>
                    <ul>
                        <li><strong>Email configurado:</strong> josemaba22@gmail.com</li>
                        <li><strong>Fecha de prueba:</strong> {date.today().strftime('%d/%m/%Y')}</li>
                        <li><strong>Sistema:</strong> Food Inventory API</li>
                        <li><strong>Estado:</strong> ✅ Operativo</li>
                    </ul>
                    
                    <h3>🔔 Próximos pasos:</h3>
                    <p>Ahora recibirás automáticamente alertas cuando tengas alimentos próximos a vencer.</p>
                    <p>Las alertas se envían diariamente a las <strong>9:00 AM</strong> si hay alimentos que vencen en los próximos <strong>3 días</strong>.</p>
                    
                    <div class="footer">
                        <p>Este es un email de prueba del sistema Food Inventory API</p>
                        <p>Si tienes alguna pregunta, revisa la documentación del sistema.</p>
                    </div>
                </body>
            </html>
            """
        })
        
        return {
            "success": True,
            "message": "✅ Email de prueba enviado exitosamente a José",
            "email_id": response.get("id"),
            "recipient": "josemaba22@gmail.com",
            "sent_at": date.today().isoformat(),
            "next_steps": "Revisa tu email (incluye carpeta de SPAM) para confirmar que llegó"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "details": "Verifica que RESEND_API_KEY esté configurada correctamente en el archivo .env",
            "troubleshooting": {
                "step_1": "Ve a https://resend.com/ y crea una cuenta",
                "step_2": "Obtén tu API Key del dashboard",
                "step_3": "Actualiza RESEND_API_KEY en el archivo .env",
                "step_4": "Reinicia el servidor"
            }
        }

@router.post("/alerts/send-to-jose/", response_model=dict)
async def send_alert_to_jose(
    days_ahead: int = Form(3, description="Días de anticipación para la alerta"),
    db: Session = Depends(get_db)
):
    """
    Enviar alerta específica a José con alimentos próximos a vencer
    
    Args:
        days_ahead: Días de anticipación (default: 3)
        db: Sesión de base de datos
    
    Returns:
        Resultado del envío del email
    """
    from app.services.auto_notification_service import get_foods_near_expiry, send_expiration_alert
    
    try:
        # Obtener alimentos próximos a vencer
        foods_near_expiry = get_foods_near_expiry(db, days_ahead)
        
        if not foods_near_expiry:
            return {
                "success": True,
                "message": "No hay alimentos próximos a vencer",
                "foods_count": 0,
                "recipient": "josemaba22@gmail.com",
                "suggestion": "Agrega algunos alimentos con fechas cercanas para probar el sistema"
            }
        
        # Enviar email específicamente a José
        result = await send_expiration_alert(foods_near_expiry, "josemaba22@gmail.com")
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando alerta a José: {str(e)}"
        )