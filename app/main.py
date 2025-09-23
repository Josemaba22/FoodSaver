from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.controllers import food_controller, category_controller, notification_controller
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.db import Base, engine, SessionLocal
from app.entities.category import Category
from app.entities.food import Food
from datetime import date
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear directorio de uploads si no existe
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs("uploads/images", exist_ok=True)
    
    # Crear tablas automáticamente si no existen
    Base.metadata.create_all(bind=engine)
    
    # Inicializar scheduler automático para alertas
    try:
        from app.services.scheduler_service import setup_scheduler_on_startup
        scheduler = setup_scheduler_on_startup()
        if scheduler:
            logger.info("✅ Sistema de alertas automáticas inicializado")
        else:
            logger.warning("⚠️  Sistema de alertas automáticas no pudo iniciarse")
    except ImportError as e:
        logger.warning(f"⚠️  No se pudo importar el scheduler (dependencias faltantes): {e}")
    except Exception as e:
        logger.error(f"❌ Error inicializando scheduler: {e}")
    
    yield
    
    # Cleanup al cerrar la aplicación
    try:
        from app.services.scheduler_service import cleanup_scheduler_on_shutdown
        cleanup_scheduler_on_shutdown()
        logger.info("🔄 Scheduler limpiado correctamente")
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"❌ Error limpiando scheduler: {e}")

app = FastAPI(
    title="Food Inventory API",
    description="API para gestión de inventario de alimentos con alertas automáticas",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar para servir archivos estáticos (imágenes)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(food_controller.router)
app.include_router(category_controller.router)
app.include_router(notification_controller.router)

# Endpoint de estado del sistema de alertas
@app.get("/system/alerts-status")
async def get_system_alerts_status():
    """
    Obtener estado general del sistema de alertas automáticas
    """
    try:
        from app.services.scheduler_service import get_scheduler_status
        from app.services.auto_notification_service import get_notification_status
        
        scheduler_status = get_scheduler_status()
        notification_status = get_notification_status()
        
        return {
            "system": "Food Inventory API",
            "alerts_system": {
                "scheduler": scheduler_status,
                "notifications": notification_status
            },
            "status": "operational" if scheduler_status.get("running") else "partial"
        }
        
    except ImportError:
        return {
            "system": "Food Inventory API",
            "alerts_system": {
                "status": "disabled",
                "reason": "Dependencias no instaladas"
            },
            "status": "limited"
        }
    except Exception as e:
        return {
            "system": "Food Inventory API", 
            "alerts_system": {
                "status": "error",
                "error": str(e)
            },
            "status": "error"
        }