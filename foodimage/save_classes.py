# save_classes.py
import tensorflow as tf
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "modelo_frutas.h5"

# Cargar modelo
model = tf.keras.models.load_model(MODEL_PATH)

# Para obtener los nombres de las clases
# Necesitamos usar los datos de entrenamiento para obtener class_indices
# Aquí asumimos que guardaste un archivo JSON con las clases o lo defines manualmente

# Ejemplo de definición manual (según tu lista anterior)
class_indices = {
    'apple': 0, 'banana': 1, 'beetroot': 2, 'bell pepper': 3, 'cabbage': 4,
    'capsicum': 5, 'carrot': 6, 'cauliflower': 7, 'chilli pepper': 8, 'corn': 9,
    'cucumber': 10, 'eggplant': 11, 'garlic': 12, 'ginger': 13, 'grapes': 14,
    'jalepeno': 15, 'kiwi': 16, 'lemon': 17, 'lettuce': 18, 'mango': 19,
    'onion': 20, 'orange': 21, 'paprika': 22, 'pear': 23, 'peas': 24,
    'pineapple': 25, 'pomegranate': 26, 'potato': 27, 'raddish': 28,
    'soy beans': 29, 'spinach': 30, 'sweetcorn': 31, 'sweetpotato': 32,
    'tomato': 33, 'turnip': 34, 'watermelon': 35
}

# Guardar en un archivo JSON para usar después en predict_model.py
import json
with open(Path(__file__).parent / "class_indices.json", "w") as f:
    json.dump(class_indices, f, indent=4)

print("✅ Clases guardadas en 'class_indices.json'")
print(class_indices)
