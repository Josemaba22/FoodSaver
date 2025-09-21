import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
import shutil
from typing import Optional

# Configuración de directorios
UPLOAD_DIR = Path("uploads/images")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def ensure_upload_directory():
    """Asegura que el directorio de uploads exista"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def save_image(file: UploadFile) -> str:
    """
    Guarda una imagen en el directorio uploads/images y retorna la URL de acceso
    
    Args:
        file: Archivo de imagen subido
        
    Returns:
        str: URL relativa de la imagen guardada
        
    Raises:
        HTTPException: Si el archivo no es válido
    """
    # Validar tipo de archivo
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no permitido. Permitidos: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Validar tamaño del archivo
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Máximo permitido: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Asegurar que el directorio existe
    ensure_upload_directory()
    
    # Generar nombre único para evitar conflictos
    file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        # Guardar archivo físicamente
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Retornar URL de acceso relativa
        return f"/uploads/images/{unique_filename}"
        
    except Exception as e:
        # Si hay error, intentar limpiar el archivo parcial
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Error guardando la imagen: {str(e)}"
        )

def delete_image(image_url: Optional[str]) -> bool:
    """
    Elimina una imagen del servidor
    
    Args:
        image_url: URL de la imagen a eliminar
        
    Returns:
        bool: True si se eliminó exitosamente, False si no se encontró
    """
    if not image_url:
        return False
        
    try:
        # Extraer nombre del archivo de la URL
        filename = image_url.split("/")[-1]
        file_path = UPLOAD_DIR / filename
        
        # Eliminar si existe
        if file_path.exists():
            file_path.unlink()
            return True
        return False
        
    except Exception:
        return False

def get_image_info(image_url: Optional[str]) -> dict:
    """
    Obtiene información sobre una imagen guardada
    
    Args:
        image_url: URL de la imagen
        
    Returns:
        dict: Información de la imagen (existe, tamaño, etc.)
    """
    if not image_url:
        return {"exists": False}
        
    try:
        filename = image_url.split("/")[-1]
        file_path = UPLOAD_DIR / filename
        
        if file_path.exists():
            stat = file_path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "filename": filename,
                "path": str(file_path)
            }
        else:
            return {"exists": False}
            
    except Exception:
        return {"exists": False, "error": True}