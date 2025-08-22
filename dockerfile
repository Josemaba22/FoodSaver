# Imagen base oficial de Python
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt .

# Instala las dependencias
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Puerto
EXPOSE 8383

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8383"]
