"""Prueba el modelo con una imagen o con la cámara. Viene de `AI.ipynb`.

Uso:
    python predict.py imagen RUTA_DE_IMAGEN [--model RUTA_DEL_MODELO]
    python predict.py camara [--index 0] [--model RUTA_DEL_MODELO]

En la cámara se sale con la tecla `q`.
"""

import argparse
import os

import numpy as np

# Mismo orden que flasky/app/detection.py: el alfabético de las carpetas del dataset.
CLASS_LABELS = (
    "Arma blanca",
    "Arma corta",
    "Arma larga",
    "Ataque de perro",
    "Choques",
    "Encañonamiento",
    "Forcejeos",
    "Golpe",
    "Incendio",
    "Normalidad",
    "Patada",
    "Persona herida",
)
INPUT_SIZE = (256, 256)
DEFAULT_MODEL = os.path.join(os.path.dirname(__file__), "..", "Aria.keras")
# En la cámara solo se muestra una amenaza si el modelo está así de seguro.
CAMERA_MIN_CERTAINTY = 0.90


def prepare(rgb_image: np.ndarray) -> np.ndarray:
    """Deja una imagen como la espera el modelo: 256 × 256, valores de 0 a 1 y en lote de uno.

    Args:
        rgb_image: Imagen de 256 × 256 en RGB.

    Returns:
        El arreglo listo para `model.predict`.
    """
    return np.expand_dims(rgb_image.astype("float32") / 255.0, axis=0)


def predict_image(model, path: str) -> None:
    """Clasifica una imagen y muestra la clase con su certeza.

    Args:
        model: Modelo de Keras ya cargado.
        path: Ruta de la imagen.
    """
    from tensorflow.keras.preprocessing import image

    img = image.img_to_array(image.load_img(path, target_size=INPUT_SIZE))
    predictions = model.predict(prepare(img), verbose=0)[0]
    best = int(np.argmax(predictions))
    print(f"Clase: {CLASS_LABELS[best]} (índice {best}), certeza: {predictions[best]:.2f}")


def predict_camera(model, index: int) -> None:
    """Clasifica cada cuadro de la cámara y lo muestra en una ventana.

    Args:
        model: Modelo de Keras ya cargado.
        index: Número de la cámara en OpenCV.
    """
    import cv2

    capture = cv2.VideoCapture(index)
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            # OpenCV entrega BGR; el modelo se probó con imágenes RGB.
            rgb = cv2.cvtColor(cv2.resize(frame, INPUT_SIZE), cv2.COLOR_BGR2RGB)
            predictions = model.predict(prepare(rgb), verbose=0)[0]
            best = int(np.argmax(predictions))
            label = CLASS_LABELS[best] if predictions[best] > CAMERA_MIN_CERTAINTY else "Normalidad"
            cv2.putText(frame, f"{label} ({predictions[best]:.2f})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.imshow("AlertAI", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


def main() -> None:
    """Lee los argumentos y corre la prueba elegida."""
    parser = argparse.ArgumentParser(description="Prueba el modelo de AlertAI")
    parser.add_argument("--model", default=os.environ.get("ALERTAI_MODEL_PATH", DEFAULT_MODEL))
    modes = parser.add_subparsers(dest="mode", required=True)
    one = modes.add_parser("imagen", help="Clasifica una imagen")
    one.add_argument("path")
    live = modes.add_parser("camara", help="Clasifica la cámara en vivo")
    live.add_argument("--index", type=int, default=0)
    args = parser.parse_args()

    from tensorflow.keras.models import load_model

    model = load_model(args.model)
    if args.mode == "imagen":
        predict_image(model, args.path)
    else:
        predict_camera(model, args.index)


if __name__ == "__main__":
    main()
