import tensorflow as tf
from tensorflow.keras.preprocessing import image
from pathlib import Path
import numpy as np
import json

# Rutas
MODEL_PATH = Path(__file__).resolve().parent / "modelo_frutas.h5"
CLASS_JSON = Path(__file__).resolve().parent / "class_indices.json"

# Cargar modelo
model = tf.keras.models.load_model(MODEL_PATH)

# Cargar clases
with open(CLASS_JSON, "r") as f:
    class_indices = json.load(f)

# Crear diccionario inverso {indice: nombre}
idx_to_class = {v: k for k, v in class_indices.items()}

# Función para preprocesar la imagen
def prep_image(img_path, target_size=(224,224)):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0  # normalizar
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# Función para predecir
def predict(img_path):
    img_array = prep_image(img_path)
    preds = model.predict(img_array)
    class_idx = np.argmax(preds[0])
    class_name = idx_to_class[class_idx]
    confidence = preds[0][class_idx]
    return {"label": class_name, "confidence": float(confidence)}

# Prueba
if __name__ == "__main__":
    # Ruta correcta
    test_img = Path(__file__).resolve().parent.parent / "dataset" / "test" / "cucumber" / "Image_1.jpg"
    result = predict(test_img)
    print("Predicción:", result)
