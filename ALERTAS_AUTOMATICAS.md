# 🚨 **Sistema de Alertas Automáticas para Food Inventory API**

## 📋 **Características del Sistema**

✅ **Detección automática** de alimentos próximos a vencer  
✅ **Envío automático de emails** con alertas diarias  
✅ **Scheduler programable** que se ejecuta todos los días  
✅ **Endpoints para gestión manual** de alertas  
✅ **Configuración flexible** mediante variables de entorno  
✅ **Sistema robusto** con manejo de errores  

---

## ⚙️ **1. Configuración Inicial**

### **1.1 Configurar Variables de Entorno**

Edita el archivo `.env` con tus datos reales:

```bash
# ===== CONFIGURACIÓN DE EMAIL =====
RESEND_API_KEY=re_your_actual_api_key_here
ADMIN_EMAIL=tuemailpersonal@gmail.com
FROM_EMAIL=noreply@tudominio.com
APP_NAME=Food Inventory System

# ===== CONFIGURACIÓN DE ALERTAS AUTOMÁTICAS =====
AUTO_ALERTS_ENABLED=true
ALERT_DAYS_AHEAD=3
ALERT_SCHEDULE_HOUR=7
ALERT_SCHEDULE_MINUTE=21

# ===== BASE DE DATOS =====
DATABASE_URL=mysql+pymysql://user:password@localhost/food_inventory
```

### **1.2 Configurar Servicio de Email (Resend)**

1. **Regístrate en Resend**: https://resend.com/
2. **Verifica tu dominio** (o usa el sandbox para pruebas)
3. **Obtén tu API Key** del dashboard
4. **Actualiza** `RESEND_API_KEY` en el archivo `.env`

---

## 🏃‍♂️ **2. Ejecutar el Sistema**

### **2.1 Iniciar la API**

```bash
cd "d:\PROTOTIPO-APP-IA\FoodInventaoryAPI"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **2.2 Verificar que funcione**

El sistema iniciará automáticamente y verás estos mensajes en los logs:

```
✅ Servicio de email configurado correctamente
✅ Scheduler iniciado exitosamente
📅 Alertas programadas para las 09:00 cada día
📧 Emails se enviarán a: tuemailpersonal@gmail.com
✅ Sistema de alertas automáticas inicializado
```

---

## 🧪 **3. Probar el Sistema**

### **3.1 Verificar Estado del Sistema**

```bash
# Estado general del sistema
curl http://localhost:8000/system/alerts-status

# Estado específico de alertas
curl http://localhost:8000/foods/alerts/status/

# Estado del scheduler
curl http://localhost:8000/foods/alerts/scheduler-status/
```

### **3.2 Probar Detección de Alimentos**

```bash
# Ver qué alimentos vencen en 7 días
curl "http://localhost:8000/foods/alerts/check/?days_ahead=7"
```

### **3.3 Enviar Alerta Manual**

```bash
# Enviar email de prueba
curl -X POST "http://localhost:8000/foods/alerts/send-manual/" \
  -F "recipient_email=tuemailpersonal@gmail.com" \
  -F "days_ahead=3"
```

### **3.4 Probar Scheduler Automático**

```bash
# Ejecutar una vez el proceso automático
curl -X POST "http://localhost:8000/foods/alerts/send-auto/"

# Probar el scheduler
curl -X POST "http://localhost:8000/foods/alerts/test-scheduler/"
```

---

## 📊 **4. Endpoints Disponibles**

### **📋 Información y Estado**
- `GET /system/alerts-status` - Estado general del sistema
- `GET /foods/alerts/status/` - Estado de notificaciones  
- `GET /foods/alerts/scheduler-status/` - Estado del scheduler
- `GET /foods/alerts/check/?days_ahead=N` - Verificar alimentos próximos a vencer

### **📧 Envío de Alertas**
- `POST /foods/alerts/send-manual/` - Enviar alerta manual
- `POST /foods/alerts/send-auto/` - Disparar proceso automático
- `POST /foods/alerts/test-scheduler/` - Probar scheduler

---

## ⏰ **5. Funcionamiento Automático**

### **¿Cuándo se envían las alertas?**

- **Todos los días** a las **9:00 AM** (configurable)
- **Solo si hay alimentos** próximos a vencer
- Se verifica automáticamente **alimentos que vencen en 3 días** (configurable)

### **¿Qué incluye el email?**

- 📊 **Tabla detallada** con alimentos próximos a vencer
- ⏰ **Días restantes** hasta el vencimiento  
- 📂 **Categoría** de cada alimento
- 🚨 **Alertas de urgencia** para alimentos críticos
- 📋 **Recomendaciones** de acción

### **Ejemplo de Email Recibido:**

```
🍎 Alerta de Alimentos - Food Inventory System
Fecha: 23/09/2025

🚨 ¡URGENTE! 2 alimento(s) vence(n) HOY o mañana.

Los siguientes 5 alimentos están próximos a vencer:

🥗 Alimento | 📅 Fecha de Vencimiento | ⏰ Días Restantes | 📂 Categoría
-----------|----------------------|------------------|------------
🚨 Manzana  | 24/09/2025          | 1 día            | Frutas
⚠️ Banana   | 25/09/2025          | 2 días           | Frutas
📅 Tomate   | 26/09/2025          | 3 días           | Verduras

📋 Recomendaciones:
• Revisa tu inventario y planifica las comidas
• Consume primero los alimentos que vencen antes
• Considera compartir o donar alimentos que no uses
```

---

## 🔧 **6. Personalización**

### **Cambiar Horario de Alertas**

Modifica en `.env`:
```bash
ALERT_SCHEDULE_HOUR=15    # 3:00 PM
ALERT_SCHEDULE_MINUTE=30  # y 30 minutos
```

### **Cambiar Días de Anticipación**

```bash
ALERT_DAYS_AHEAD=5  # Alertar con 5 días de anticipación
```

### **Deshabilitar Alertas Automáticas**

```bash
AUTO_ALERTS_ENABLED=false
```

---

## 📱 **7. Monitoreo y Logs**

### **Ver Logs en Tiempo Real**

Los logs del sistema mostrarán:

```
🔄 Iniciando verificación automática de alimentos...
🔍 Encontrados 3 alimentos próximos a vencer en 3 días
✅ Email enviado exitosamente a admin@tudominio.com
✅ Alerta automática enviada exitosamente: 3 alimentos
```

### **Solución de Problemas Comunes**

| Problema | Solución |
|----------|----------|
| No llegan emails | Verificar RESEND_API_KEY y FROM_EMAIL |
| Scheduler no inicia | Verificar AUTO_ALERTS_ENABLED=true |
| Error de zona horaria | Ajustar timezone en scheduler_service.py |
| Base de datos vacía | Agregar alimentos de prueba |

---

## 🎯 **¡Sistema Listo!**

Una vez configurado correctamente:

✅ **Las alertas se enviarán automáticamente** cada día  
✅ **Recibirás emails** cuando haya alimentos próximos a vencer  
✅ **Puedes gestionar alertas manualmente** usando los endpoints  
✅ **El sistema funciona 24/7** mientras la API esté ejecutándose  

**¡Tu inventario de alimentos nunca volverá a tener desperdicios por olvido!** 🎉