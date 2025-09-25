import sys
from pathlib import Path
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

# Ruta del modelo
MODEL_PATH = Path(__file__).resolve().parent / "modelo_frutas.h5"

# Cargar modelo
model = tf.keras.models.load_model(MODEL_PATH)

# Clases guardadas (asegúrate de que coincidan con train_data.class_indices)
# Versión original en inglés (comentada para referencia):
# class_indices = {
#     'apple': 0, 'banana': 1, 'beetroot': 2, 'bell pepper': 3, 'cabbage': 4,
#     'capsicum': 5, 'carrot': 6, 'cauliflower': 7, 'chilli pepper': 8, 'corn': 9,
#     'cucumber': 10, 'eggplant': 11, 'garlic': 12, 'ginger': 13, 'grapes': 14,
#     'jalepeno': 15, 'kiwi': 16, 'lemon': 17, 'lettuce': 18, 'mango': 19,
#     'onion': 20, 'orange': 21, 'paprika': 22, 'pear': 23, 'peas': 24,
#     'pineapple': 25, 'pomegranate': 26, 'potato': 27, 'raddish': 28,
#     'soy beans': 29, 'spinach': 30, 'sweetcorn': 31, 'sweetpotato': 32,
#     'tomato': 33, 'turnip': 34, 'watermelon': 35
# }

# Versión en español (activa):
class_indices = {
    'manzana': 0, 'banana': 1, 'remolacha': 2, 'pimiento': 3, 'repollo': 4,
    'pimiento morrón': 5, 'zanahoria': 6, 'coliflor': 7, 'chile': 8, 'maíz': 9,
    'pepino': 10, 'berenjena': 11, 'ajo': 12, 'jengibre': 13, 'uvas': 14,
    'jalapeño': 15, 'kiwi': 16, 'limón': 17, 'lechuga': 18, 'mango': 19,
    'cebolla': 20, 'naranja': 21, 'pimentón': 22, 'pera': 23, 'guisantes': 24,
    'piña': 25, 'granada': 26, 'papa': 27, 'rábano': 28,
    'frijoles de soya': 29, 'espinaca': 30, 'maíz dulce': 31, 'batata': 32,
    'tomate': 33, 'nabo': 34, 'sandía': 35
}

# Crear diccionario inverso para convertir índice → nombre de clase
idx_to_class = {v: k for k, v in class_indices.items()}


def prep_image(img_path, target_size=(224, 224)):
    """Carga y preprocesa la imagen para la predicción"""
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0
    return img_array


def predict_image(img_path):
    img_array = prep_image(img_path)
    preds = model.predict(img_array)[0]
    class_idx = np.argmax(preds)
    class_name = idx_to_class[class_idx]
    confidence = preds[class_idx]
    return {"label": class_name, "confidence": float(confidence)}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python predict_image.py <ruta_imagen>")
        sys.exit(1)

    img_path = Path(sys.argv[1])
    if not img_path.exists():
        print(f"❌ La imagen {img_path} no existe")
        sys.exit(1)

    result = predict_image(img_path)
    print(f"✅ Predicción: {result['label']} con confianza {result['confidence']:.4f}")
