"""Entrena de nuevo el modelo de AlertAI (Aria.keras).

El código original se perdió. Esta es una reconstrucción:
- La arquitectura, el optimizador, la pérdida y la métrica son exactamente los que trae guardados
  Aria.keras (se leyeron de su config.json).
- El tamaño de lote, las épocas y la división entre entrenamiento y validación son supuestos.

El dataset debe tener una carpeta por clase. Keras numera las clases en orden alfabético, así
que los nombres deben dar el mismo orden que CLASS_LABELS en flasky/app/detection.py: "Arma blanca",
"Arma corta", ..., "Normalidad", "Patada", "Persona herida".

Uso:
    python train.py RUTA_DEL_DATASET [--epochs 20] [--output Aria.keras]
"""

import argparse

import tensorflow as tf
from tensorflow.keras import layers, models

IMAGE_SIZE = (256, 256)
NUM_CLASSES = 12
BATCH_SIZE = 32
VALIDATION_SPLIT = 0.2
SEED = 123
DROPOUT = 0.2


def build_model() -> tf.keras.Model:
    """Arma la red neuronal convolucional con las mismas capas que Aria.keras.

    Returns:
        El modelo compilado.
    """
    def conv(filters, strides=1):
        """Una convolución de 2×2 con ReLU seguida de normalización por lotes."""
        return [layers.Conv2D(filters, (2, 2), strides=strides, activation="relu"), layers.BatchNormalization()]

    stack = [layers.Input(shape=(*IMAGE_SIZE, 3))]
    stack += conv(32) + conv(64, strides=2) + [layers.MaxPooling2D(), layers.Dropout(DROPOUT)]
    stack += conv(128) + [layers.MaxPooling2D(), layers.Dropout(DROPOUT)]
    stack += conv(128) + conv(256) + [layers.MaxPooling2D(), layers.Dropout(DROPOUT)]
    stack += conv(256) + conv(128) + [layers.MaxPooling2D(), layers.Dropout(DROPOUT)]
    stack += conv(64) + conv(32) + [layers.MaxPooling2D()]
    stack += [layers.Flatten(), layers.Dropout(DROPOUT), layers.Dense(32, activation="relu"),
              layers.Dense(NUM_CLASSES, activation="softmax")]

    model = models.Sequential(stack, name="aria")
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def load_datasets(data_dir: str):
    """Carga el dataset y lo divide en entrenamiento y validación, con valores de 0 a 1.

    Args:
        data_dir: Carpeta con una subcarpeta por clase.

    Returns:
        Los datos de entrenamiento, los de validación y los nombres de las clases.
    """
    def load(subset):
        """Carga una parte del dataset: `training` o `validation`."""
        return tf.keras.utils.image_dataset_from_directory(
            data_dir, subset=subset, validation_split=VALIDATION_SPLIT, seed=SEED,
            image_size=IMAGE_SIZE, batch_size=BATCH_SIZE)

    train = load("training")
    validation = load("validation")
    class_names = train.class_names

    # La app divide entre 255 antes de predecir; el modelo no lo hace por dentro.
    def scale(images, labels):
        """Pasa los pixeles de 0-255 a 0-1."""
        return images / 255.0, labels

    autotune = tf.data.AUTOTUNE
    return (train.map(scale).prefetch(autotune), validation.map(scale).prefetch(autotune), class_names)


def main() -> None:
    """Entrena, guarda el mejor modelo y deja registros para TensorBoard."""
    parser = argparse.ArgumentParser(description="Entrena el modelo de AlertAI")
    parser.add_argument("data_dir", help="Carpeta con una subcarpeta por clase")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--output", default="Aria.keras")
    parser.add_argument("--logs", default="logs", help="Carpeta para TensorBoard")
    args = parser.parse_args()

    train, validation, class_names = load_datasets(args.data_dir)
    if len(class_names) != NUM_CLASSES:
        raise SystemExit(f"Se esperaban {NUM_CLASSES} clases y hay {len(class_names)}: {class_names}")
    print("Clases, en el orden que usará el modelo:")
    for index, name in enumerate(class_names):
        print(f"  {index}: {name}")

    model = build_model()
    model.summary()
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(args.output, monitor="val_accuracy", save_best_only=True),
        tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True),
        tf.keras.callbacks.TensorBoard(log_dir=args.logs),
    ]
    model.fit(train, validation_data=validation, epochs=args.epochs, callbacks=callbacks)
    print(f"Modelo guardado en {args.output}. Para ver las gráficas: tensorboard --logdir {args.logs}")


if __name__ == "__main__":
    main()
