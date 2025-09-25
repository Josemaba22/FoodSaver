# foodimage/train_model.py
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pathlib import Path
from foodimage.utils import proc_img

def train_food_model(epochs=5):
    # Rutas (ajustadas)
    train_path = Path("dataset/train")
    val_path   = Path("dataset/validation")

    # Crear listas de archivos
    train_files = list(train_path.glob("**/*.jpg"))
    val_files   = list(val_path.glob("**/*.jpg"))

    # Crear DataFrames con Filepath y Label
    train_df = proc_img(train_files)
    val_df   = proc_img(val_files)

    # Generadores de imágenes
    train_datagen = ImageDataGenerator(rescale=1./255)
    val_datagen   = ImageDataGenerator(rescale=1./255)

    train_data = train_datagen.flow_from_dataframe(
        train_df,
        x_col="Filepath",
        y_col="Label",
        target_size=(224,224),
        class_mode="categorical"
    )

    val_data = val_datagen.flow_from_dataframe(
        val_df,
        x_col="Filepath",
        y_col="Label",
        target_size=(224,224),
        class_mode="categorical"
    )
    print("Diccionario de clases:", train_data.class_indices)
    # Número de clases
    num_classes = len(train_data.class_indices)

    # TinyVGG
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(10, 3, activation="relu", input_shape=(224,224,3)),
        tf.keras.layers.Conv2D(10, 3, activation="relu"),
        tf.keras.layers.MaxPool2D(2),

        tf.keras.layers.Conv2D(10, 3, activation="relu"),
        tf.keras.layers.Conv2D(10, 3, activation="relu"),
        tf.keras.layers.MaxPool2D(2),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(num_classes, activation="softmax")
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    # Entrenar
    history = model.fit(
        train_data,
        validation_data=val_data,
        epochs=epochs
    )

    # Guardar modelo
    MODEL_PATH = Path(__file__).resolve().parent / "modelo_frutas.h5"
    model.save(MODEL_PATH)
    print(f"✅ Modelo guardado en {MODEL_PATH}")

if __name__ == "__main__":
    train_food_model(epochs=5)
