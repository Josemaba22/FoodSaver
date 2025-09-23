"""
Scheduler Automático para Alertas de Alimentos
Configura y ejecuta tareas programadas para envío automático de alertas
"""
import os
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.auto_notification_service import auto_send_daily_alert, get_notification_status
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del scheduler
ALERT_SCHEDULE_HOUR = int(os.getenv("ALERT_SCHEDULE_HOUR", "9"))  # 9 AM por defecto
ALERT_SCHEDULE_MINUTE = int(os.getenv("ALERT_SCHEDULE_MINUTE", "0"))  # En punto
AUTO_ALERTS_ENABLED = os.getenv("AUTO_ALERTS_ENABLED", "true").lower() == "true"

# Instancia global del scheduler
scheduler = None

async def scheduled_alert_task():
    """
    Tarea programada que se ejecuta automáticamente cada día
    """
    try:
        logger.info("🕒 Ejecutando tarea programada de alertas...")
        
        # Ejecutar la función de alerta automática
        result = await auto_send_daily_alert()
        
        if result["success"]:
            if result.get("foods_count", 0) > 0:
                logger.info(f"✅ Alerta automática enviada exitosamente: {result['foods_count']} alimentos")
            else:
                logger.info("✅ Verificación automática completada: No hay alimentos próximos a vencer")
        else:
            logger.error(f"❌ Error en alerta automática: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        logger.error(f"❌ Error crítico en tarea programada: {str(e)}")

def start_scheduler():
    """
    Inicia el scheduler automático
    """
    global scheduler
    
    if not AUTO_ALERTS_ENABLED:
        logger.info("📵 Scheduler de alertas automáticas deshabilitado en configuración")
        return None
    
    try:
        # Crear scheduler si no existe
        if scheduler is None:
            scheduler = AsyncIOScheduler()
        
        # Verificar estado del sistema
        status = get_notification_status()
        if not status["email_service_available"]:
            logger.warning("⚠️  Servicio de email no disponible. El scheduler no se iniciará.")
            return None
        
        # Configurar tarea diaria
        trigger = CronTrigger(
            hour=ALERT_SCHEDULE_HOUR, 
            minute=ALERT_SCHEDULE_MINUTE
            # Sin timezone para usar la hora local del sistema
        )
        
        # Agregar job al scheduler
        scheduler.add_job(
            scheduled_alert_task,
            trigger=trigger,
            id="daily_food_alert",
            name="Alerta Diaria de Alimentos",
            replace_existing=True,
            max_instances=1
        )
        
        # Iniciar scheduler
        scheduler.start()
        
        logger.info(f"✅ Scheduler iniciado exitosamente")
        logger.info(f"📅 Alertas programadas para las {ALERT_SCHEDULE_HOUR:02d}:{ALERT_SCHEDULE_MINUTE:02d} cada día")
        logger.info(f"📧 Emails se enviarán a: {status['admin_email']}")
        
        return scheduler
        
    except Exception as e:
        logger.error(f"❌ Error iniciando scheduler: {str(e)}")
        return None

def stop_scheduler():
    """
    Detiene el scheduler automático
    """
    global scheduler
    
    try:
        if scheduler and scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("⏹️  Scheduler detenido exitosamente")
        else:
            logger.info("ℹ️  Scheduler no estaba ejecutándose")
            
    except Exception as e:
        logger.error(f"❌ Error deteniendo scheduler: {str(e)}")

def get_scheduler_status() -> dict:
    """
    Obtiene el estado actual del scheduler
    
    Returns:
        Estado del scheduler y próximas ejecuciones
    """
    global scheduler
    
    try:
        if not scheduler:
            return {
                "running": False,
                "enabled": AUTO_ALERTS_ENABLED,
                "error": "Scheduler no inicializado"
            }
        
        jobs = scheduler.get_jobs()
        alert_job = next((job for job in jobs if job.id == "daily_food_alert"), None)
        
        status = {
            "running": scheduler.running if scheduler else False,
            "enabled": AUTO_ALERTS_ENABLED,
            "schedule_hour": ALERT_SCHEDULE_HOUR,
            "schedule_minute": ALERT_SCHEDULE_MINUTE,
            "job_exists": alert_job is not None,
            "next_run": None,
            "last_run": None
        }
        
        if alert_job:
            status["next_run"] = alert_job.next_run_time.isoformat() if alert_job.next_run_time else None
            # APScheduler no guarda last_run_time por defecto, pero podemos obtenerlo del log
            
        return status
        
    except Exception as e:
        return {
            "running": False,
            "enabled": AUTO_ALERTS_ENABLED,
            "error": str(e)
        }

async def test_scheduler():
    """
    Función de prueba para verificar que el scheduler funciona correctamente
    """
    logger.info("🧪 Ejecutando prueba del scheduler...")
    
    try:
        # Ejecutar una vez la tarea de alerta para probar
        result = await scheduled_alert_task()
        
        logger.info("✅ Prueba del scheduler completada")
        return {
            "success": True,
            "message": "Prueba de scheduler ejecutada correctamente",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error en prueba del scheduler: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Funciones para integrar con FastAPI
def setup_scheduler_on_startup():
    """
    Función para llamar al iniciar la aplicación FastAPI
    """
    logger.info("🚀 Configurando scheduler en startup de la aplicación...")
    return start_scheduler()

def cleanup_scheduler_on_shutdown():
    """
    Función para llamar al cerrar la aplicación FastAPI
    """
    logger.info("🔄 Limpiando scheduler en shutdown de la aplicación...")
    stop_scheduler()