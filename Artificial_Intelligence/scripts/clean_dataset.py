"""Limpia un dataset de imágenes antes de entrenar: quita formatos raros, duplicados y renombra.

Viene de `pipeline.ipynb`. Espera una carpeta con una subcarpeta por clase, por ejemplo
`dataset/Incendios/`, `dataset/Golpe/`. Modifica los archivos en su lugar: haz un respaldo antes.

Uso:
    python clean_dataset.py RUTA_DEL_DATASET [--prefix IMAGEN]
"""

import argparse
import hashlib
import os

from PIL import Image

VALID_FORMATS = {"jpeg", "jpg", "bmp", "png"}


def remove_invalid_images(data_dir: str) -> int:
    """Borra los archivos que no son una imagen en un formato aceptado.

    Args:
        data_dir: Carpeta del dataset.

    Returns:
        Cuántos archivos se borraron.
    """
    removed = 0
    for image_class in os.listdir(data_dir):
        class_dir = os.path.join(data_dir, image_class)
        if not os.path.isdir(class_dir):
            continue
        for name in os.listdir(class_dir):
            path = os.path.join(class_dir, name)
            try:
                with Image.open(path) as img:
                    image_format = (img.format or "").lower()
            except Exception:
                image_format = ""
            if image_format not in VALID_FORMATS:
                print(f"Se borra (formato no válido): {path}")
                os.remove(path)
                removed += 1
    return removed


def remove_duplicates(data_dir: str) -> int:
    """Borra las imágenes repetidas, comparando su contenido.

    Args:
        data_dir: Carpeta del dataset.

    Returns:
        Cuántas imágenes repetidas se borraron.
    """
    seen = set()
    removed = 0
    for image_class in os.listdir(data_dir):
        class_dir = os.path.join(data_dir, image_class)
        if not os.path.isdir(class_dir):
            continue
        for name in os.listdir(class_dir):
            path = os.path.join(class_dir, name)
            with open(path, "rb") as file:
                digest = hashlib.sha1(file.read()).digest()
            if digest in seen:
                os.remove(path)
                removed += 1
            else:
                seen.add(digest)
    return removed


def rename_images(data_dir: str, prefix: str) -> None:
    """Renombra las imágenes de cada clase como PREFIJOV1.jpg, PREFIJOV2.jpg, etc.

    Args:
        data_dir: Carpeta del dataset.
        prefix: Texto con el que empieza cada nombre.
    """
    for image_class in os.listdir(data_dir):
        class_dir = os.path.join(data_dir, image_class)
        if not os.path.isdir(class_dir):
            continue
        for count, name in enumerate(sorted(os.listdir(class_dir)), start=1):
            os.rename(os.path.join(class_dir, name), os.path.join(class_dir, f"{prefix}V{count}.jpg"))


def main() -> None:
    """Corre los tres pasos en orden."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("data_dir", help="Carpeta con una subcarpeta por clase")
    parser.add_argument("--prefix", default="IMAGEN", help="Prefijo para renombrar las imágenes")
    args = parser.parse_args()

    print(f"Archivos no válidos borrados: {remove_invalid_images(args.data_dir)}")
    print(f"Duplicados borrados: {remove_duplicates(args.data_dir)}")
    rename_images(args.data_dir, args.prefix)
    print("Imágenes renombradas.")


if __name__ == "__main__":
    main()
