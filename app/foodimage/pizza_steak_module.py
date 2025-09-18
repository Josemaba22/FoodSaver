import tensorflow as tf
import matplotlib.pyplot as plt

class PizzaSteakClassifier:
    def __init__(self, model_path="foodimage/modelo_pizza_steak.h5", img_shape=224):
        self.img_shape = img_shape
        self.class_names = ['pizza', 'steak']
        self.model = tf.keras.models.load_model(model_path)

    def predict_image(self, filename, save_plot=False):
        img = tf.io.read_file(filename)
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.resize(img, size=[self.img_shape, self.img_shape])
        img = img / 255.0

        pred = self.model.predict(tf.expand_dims(img, axis=0))
        pred_class = self.class_names[int(tf.round(pred)[0][0])]

        plt.imshow(img)
        plt.title(f"Prediction: {pred_class}")
        plt.axis(False)

        if save_plot:
            save_path = f"foofimage/docs/{filename.split('/')[-1]}"
            plt.savefig(save_path)

        return pred_class, pred
