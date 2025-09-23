"""
Servicio de Notificaciones Automáticas
Maneja el envío automático de alertas por email para alimentos próximos a vencer
"""
import os
import asyncio
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.entities.food import Food
from app.config.db import SessionLocal
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import resend
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configuración de email
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@example.com")
    APP_NAME = os.getenv("APP_NAME", "Food Inventory System")
    
    # Configuración de alertas
    AUTO_ALERTS_ENABLED = os.getenv("AUTO_ALERTS_ENABLED", "true").lower() == "true"
    ALERT_DAYS_AHEAD = int(os.getenv("ALERT_DAYS_AHEAD", "3"))
    
    # Configurar API key de Resend
    if RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
        resend_available = True
        logger.info("✅ Servicio de email configurado correctamente")
    else:
        resend_available = False
        logger.warning("⚠️  Resend API Key no configurada. Las alertas por email no funcionarán.")
        
except ImportError as e:
    logger.error(f"❌ Error importando dependencias: {e}")
    resend_available = False
    # Configurar valores por defecto para evitar errores
    RESEND_API_KEY = None
    ADMIN_EMAIL = "admin@example.com"
    FROM_EMAIL = "noreply@example.com"
    APP_NAME = "Food Inventory System"
    AUTO_ALERTS_ENABLED = False
    ALERT_DAYS_AHEAD = 3
except Exception as e:
    logger.error(f"❌ Error configurando servicio de email: {e}")
    resend_available = False
    # Configurar valores por defecto para evitar errores
    RESEND_API_KEY = None
    ADMIN_EMAIL = "admin@example.com"
    FROM_EMAIL = "noreply@example.com"
    APP_NAME = "Food Inventory System"
    AUTO_ALERTS_ENABLED = False
    ALERT_DAYS_AHEAD = 3

def get_foods_near_expiry(db: Session, days_ahead: int = None) -> List[Food]:
    """
    Obtiene alimentos que vencen en los próximos N días (incluye alimentos ya vencidos)
    
    Args:
        db: Sesión de base de datos
        days_ahead: Días de anticipación (default desde config)
    
    Returns:
        Lista de alimentos próximos a vencer o ya vencidos
    """
    if days_ahead is None:
        days_ahead = ALERT_DAYS_AHEAD
        
    # Fecha límite futura (hoy + días de anticipación)
    future_cutoff_date = date.today() + timedelta(days=days_ahead)
    
    # Fecha límite pasada (para incluir alimentos vencidos hace hasta 7 días)
    past_cutoff_date = date.today() - timedelta(days=7)
    
    # Buscar alimentos que vencen desde hace una semana hasta la fecha límite futura
    foods = db.query(Food).filter(
        Food.admission_date >= past_cutoff_date,
        Food.admission_date <= future_cutoff_date
    ).all()
    
    logger.info(f"🔍 Encontrados {len(foods)} alimentos próximos a vencer o vencidos en rango de {days_ahead} días")
    return foods

async def send_expiration_alert(foods_near_expiry: List[Food], recipient_email: str = None) -> dict:
    """
    Envía alerta por email sobre alimentos próximos a vencer
    
    Args:
        foods_near_expiry: Lista de alimentos próximos a vencer
        recipient_email: Email destinatario (default: ADMIN_EMAIL)
    
    Returns:
        Resultado del envío del email
    """
    if not resend_available:
        return {
            "success": False,
            "error": "Servicio de email no configurado",
            "foods_count": len(foods_near_expiry)
        }
    
    if not recipient_email:
        recipient_email = ADMIN_EMAIL
    
    if not foods_near_expiry:
        return {
            "success": True,
            "message": "No hay alimentos próximos a vencer",
            "foods_count": 0
        }
    
    try:
        # Construir mensaje HTML simplificado (sin tablas)
        foods_html = ""
        for food in foods_near_expiry:
            days_until_expiry = (food.admission_date - date.today()).days
            alert_icon = "🚨" if days_until_expiry <= 1 else "⚠️" if days_until_expiry <= 2 else "📅"
            status_color = 'red' if days_until_expiry <= 1 else 'orange' if days_until_expiry <= 2 else 'green'
            
            foods_html += f"""
            <div style="background-color: #f9f9f9; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid {status_color};">
                <p style="margin: 5px 0; font-size: 16px;"><strong>{alert_icon} {food.name}</strong></p>
                <p style="margin: 5px 0; color: #666;">📅 Fecha de vencimiento: <strong>{food.admission_date}</strong></p>
                <p style="margin: 5px 0; color: {status_color};">⏰ Días restantes: <strong>{days_until_expiry} día{'s' if days_until_expiry != 1 else ''}</strong></p>
                <p style="margin: 5px 0; color: #666;">📂 Categoría: {food.category.name if hasattr(food, 'category') and food.category else 'Sin categoría'}</p>
            </div>
            """
        
        # Determinar urgencia del mensaje
        urgent_foods = [f for f in foods_near_expiry if (f.admission_date - date.today()).days <= 1]
        urgency_text = ""
        if urgent_foods:
            urgency_text = f"""
            <div style="background-color: #ffebee; border: 2px solid #d32f2f; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <p style="color: #d32f2f; font-weight: bold; font-size: 18px; margin: 0;">
                    🚨 ¡URGENTE! {len(urgent_foods)} alimento(s) vence(n) HOY o ya están vencidos
                </p>
            </div>
            """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Alerta de Alimentos</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        
        <h1 style="color: #d32f2f; text-align: center; margin-bottom: 20px; border-bottom: 3px solid #d32f2f; padding-bottom: 15px;">
            🚨 Alerta de Alimentos
        </h1>
        
        <p style="font-size: 16px; text-align: center; margin: 20px 0; color: #333;">
            <strong>📅 Fecha:</strong> {date.today().strftime('%d/%m/%Y')}
        </p>
        
        {urgency_text}
        
        <p style="font-size: 18px; margin: 25px 0; text-align: center; color: #333;">
            Tienes <strong style="color: #d32f2f; font-size: 20px;">{len(foods_near_expiry)}</strong> alimento(s) que requieren tu atención:
        </p>
        
        <div style="margin: 25px 0;">
            {foods_html}
        </div>
        
        <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 30px 0; border-left: 5px solid #4caf50;">
            <h3 style="color: #2e7d32; margin-top: 0; margin-bottom: 15px;">📋 Recomendaciones:</h3>
            <ul style="margin: 0; padding-left: 20px; color: #333;">
                <li style="margin: 8px 0;">🍽️ Revisa tu inventario y planifica las comidas</li>
                <li style="margin: 8px 0;">⏰ Consume primero los alimentos que vencen antes</li>
                <li style="margin: 8px 0;">🤝 Considera compartir o donar alimentos que no uses</li>
                <li style="margin: 8px 0;">✅ Actualiza el inventario después de consumir</li>
            </ul>
        </div>
        
        <hr style="border: none; border-top: 2px solid #eee; margin: 40px 0;">
        
        <p style="font-size: 14px; color: #888; text-align: center; margin: 0;">
            Este mensaje fue enviado automáticamente por <strong>{APP_NAME}</strong><br>
            🕒 Hora de envío: {date.today().strftime('%d/%m/%Y a las %H:%M')}
        </p>
        
    </div>
</body>
</html>
        """
        
        # Enviar email usando la nueva API de Resend
        response = resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [recipient_email],
            "subject": f"🚨 {len(foods_near_expiry)} alimento(s) próximo(s) a vencer - {APP_NAME}",
            "html": html_content
        })
        
        logger.info(f"✅ Email enviado exitosamente a {recipient_email}")
        
        return {
            "success": True,
            "message": f"Email enviado exitosamente a {recipient_email}",
            "email_id": response.get("id"),
            "foods_count": len(foods_near_expiry),
            "urgent_foods": len(urgent_foods),
            "recipient": recipient_email
        }
        
    except Exception as e:
        logger.error(f"❌ Error enviando email: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "foods_count": len(foods_near_expiry)
        }

async def auto_send_daily_alert() -> dict:
    """
    Función principal para envío automático de alertas diarias
    Se ejecuta automáticamente según el schedule configurado
    
    Returns:
        Resultado del envío automático
    """
    if not AUTO_ALERTS_ENABLED:
        logger.info("📵 Alertas automáticas deshabilitadas en configuración")
        return {"success": False, "message": "Alertas automáticas deshabilitadas"}
    
    logger.info("🔄 Iniciando verificación automática de alimentos...")
    
    # Crear sesión de base de datos
    db = SessionLocal()
    try:
        # Obtener alimentos próximos a vencer
        foods_near_expiry = get_foods_near_expiry(db, ALERT_DAYS_AHEAD)
        
        if not foods_near_expiry:
            logger.info("✅ No hay alimentos próximos a vencer")
            return {
                "success": True, 
                "message": "No hay alimentos próximos a vencer",
                "foods_count": 0,
                "check_date": date.today().isoformat()
            }
        
        # Enviar alerta automática
        result = await send_expiration_alert(foods_near_expiry, ADMIN_EMAIL)
        
        # Log del resultado
        if result["success"]:
            logger.info(f"✅ Alerta automática enviada: {result['foods_count']} alimentos")
        else:
            logger.error(f"❌ Error en alerta automática: {result.get('error', 'Error desconocido')}")
        
        result["auto_sent"] = True
        result["check_date"] = date.today().isoformat()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error en verificación automática: {str(e)}")
        return {
            "success": False,
            "error": f"Error en verificación automática: {str(e)}",
            "check_date": date.today().isoformat()
        }
    finally:
        db.close()

def get_notification_status() -> dict:
    """
    Obtiene el estado actual del sistema de notificaciones
    
    Returns:
        Estado de configuración y servicios
    """
    return {
        "email_service_available": resend_available,
        "auto_alerts_enabled": AUTO_ALERTS_ENABLED,
        "admin_email": ADMIN_EMAIL,
        "from_email": FROM_EMAIL,
        "alert_days_ahead": ALERT_DAYS_AHEAD,
        "resend_configured": RESEND_API_KEY is not None,
        "app_name": APP_NAME
    }