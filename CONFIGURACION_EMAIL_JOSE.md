# 📧 **Configuración de Email para José - Food Inventory API**

## 🚀 **¡Todo está listo! Solo necesitas la API Key de Resend**

### **📧 Tu configuración actual:**
- **Email:** josemaba_22@hotmail.com  
- **Aplicación:** Food Inventory System
- **Alertas automáticas:** ✅ Habilitadas (9:00 AM diariamente)
- **Anticipación:** 3 días antes del vencimiento

---

## 🔑 **Paso 1: Obtener API Key de Resend (5 minutos)**

### **A. Crear cuenta en Resend:**
1. Ve a: **https://resend.com/**
2. Clic en "Get Started" o "Sign Up"
3. Registrate con cualquier email (puede ser el mismo josemaba_22@hotmail.com)
4. Verifica tu email

### **B. Obtener API Key:**
1. Una vez logueado, ve al **Dashboard**
2. En el menú lateral, clic en **"API Keys"**
3. Clic en **"Create API Key"**
4. Dale un nombre: **"FoodInventory"**
5. Clic en **"Add"**
6. **¡IMPORTANTE!** Copia la API Key que empieza con `re_` (algo como: `re_123abc456def789`)

### **C. Actualizar archivo .env:**
1. Abre el archivo `.env` en tu proyecto
2. Busca la línea: `RESEND_API_KEY=re_XXXXXX_aqui_tu_api_key_real`
3. Reemplaza con tu API Key real:
   ```
   RESEND_API_KEY=re_tu_api_key_real_aqui
   ```
4. Guarda el archivo

---

## 🧪 **Paso 2: Probar el Sistema (2 minutos)**

### **A. Reiniciar el servidor:**
```bash
# Presiona Ctrl+C en la terminal donde corre uvicorn
# Luego ejecuta de nuevo:
uvicorn app.main:app --reload --port 8000
```

### **B. Probar email simple:**
**Opción 1 - Swagger UI (Recomendado):**
1. Ve a: `http://localhost:8000/docs`
2. Busca `POST /foods/alerts/test-jose/`
3. Clic en "Try it out" → "Execute"

**Opción 2 - Comando curl:**
```bash
curl -X POST "http://localhost:8000/foods/alerts/test-jose/"
```

### **C. Verificar tu email:**
- **Revisa tu bandeja de entrada:** josemaba_22@hotmail.com
- **⚠️ MUY IMPORTANTE:** Revisa también la **carpeta de SPAM/Correo No Deseado**
- **Busca un email con asunto:** "🧪 Test Email - Food Inventory para José"

---

## 🍎 **Paso 3: Probar con Alimentos Reales**

### **A. Verificar que detecta tu alimento:**
```bash
curl "http://localhost:8000/foods/alerts/check/?days_ahead=3"
```

### **B. Enviar alerta real:**
**Opción 1 - Swagger UI:**
1. Ve a: `http://localhost:8000/docs`
2. Busca `POST /foods/alerts/send-to-jose/`
3. Clic en "Try it out" → "Execute"

**Opción 2 - Comando curl:**
```bash
curl -X POST "http://localhost:8000/foods/alerts/send-to-jose/" \
  -F "days_ahead=3"
```

---

## 📋 **Endpoints Creados Específicamente Para Ti:**

| Endpoint | Función | Uso |
|----------|---------|-----|
| `POST /foods/alerts/test-jose/` | Envía email de prueba | Para verificar que funciona |
| `POST /foods/alerts/send-to-jose/` | Envía alerta real con tus alimentos | Para probar con datos reales |
| `GET /foods/alerts/check/` | Ver qué alimentos están por vencer | Para verificar sin enviar email |

---

## 🚨 **¿Problemas? Troubleshooting:**

### **Error 1: No recibo emails**
- ✅ Revisa carpeta de SPAM en Hotmail
- ✅ Verifica que la API Key sea correcta
- ✅ Reinicia el servidor después de cambiar .env

### **Error 2: "email_service_available: false"**
```bash
# Verificar estado:
curl "http://localhost:8000/foods/alerts/status/"

# Si es false, verifica .env y reinicia servidor
```

### **Error 3: API Key incorrecta**
- Ve al dashboard de Resend
- Genera una nueva API Key
- Actualiza .env

---

## 🎯 **¡Funcionamiento Automático!**

Una vez configurado:
- ✅ **Todos los días a las 9:00 AM** recibirás alertas automáticamente
- ✅ **Solo si hay alimentos** que vencen en 3 días o menos
- ✅ **En tu email:** josemaba_22@hotmail.com
- ✅ **24/7** mientras el servidor esté ejecutándose

---

## 📞 **¿Necesitas Ayuda?**

1. **Estado del sistema:** `http://localhost:8000/system/alerts-status`
2. **Documentación completa:** `http://localhost:8000/docs`
3. **Verificar logs:** Mira la consola donde ejecutaste uvicorn

**¡Tu sistema de alertas está listo para funcionar! 🎉**