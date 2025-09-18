from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pizza_steak_module import PizzaSteakClassifier
import tensorflow as tf

# Generadores
train_datagen = ImageDataGenerator(rescale=1.0/255)
val_datagen = ImageDataGenerator(rescale=1.0/255)

train_data = train_datagen.flow_from_directory(
    "foodimage/pizza_steak/train",
    target_size=(224,224),
    class_mode="binary",
    seed=42
)

val_data = val_datagen.flow_from_directory(
    "foodimage/pizza_steak/test",
    target_size=(224,224),
    class_mode="binary",
    seed=42
)

# Definir y entrenar modelo
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(224,224,3)),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    loss="binary_crossentropy",
    optimizer=tf.keras.optimizers.Adam(0.001),
    metrics=["accuracy"]
)

history = model.fit(train_data, epochs=5, validation_data=val_data)

# Guardar modelo entrenado
model.save("foodimage/modelo_pizza_steak.h5")

# Usar módulo para predicción
clf = PizzaSteakClassifier()
pred_class, pred_probs = clf.predict_image("foodimage/pizza_steak/test/pizza/example1.jpg", save_plot=True)

print("Clase predicha:", pred_class)
print("Probabilidades:", pred_probs)