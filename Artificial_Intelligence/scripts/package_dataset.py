"""Empaqueta el dataset limpio para subirlo a Kaggle.

Crea una carpeta lista para la API de Kaggle (`kaggle datasets create -p CARPETA`) o para subir el
ZIP desde la página web:

- `alertai-dataset.zip`: `images/<clase>/*.jpg`, `labels.csv` y `README.md` (la ficha del dataset).
- `dataset-metadata.json`: título, identificador y licencia que pide la API de Kaggle.

No incluye rutas de tu computadora ni el reporte de limpieza completo.

Uso:
    python package_dataset.py AlertIA-limpio --owner TU_USUARIO_DE_KAGGLE
"""

import argparse
import csv
import io
import zipfile
from itertools import groupby
from pathlib import Path

from pydantic import BaseModel, Field

DEFAULT_SLUG = "alertai-situaciones-de-riesgo"
DEFAULT_TITLE = "AlertAI: situaciones de riesgo en cámaras"


class LabeledImage(BaseModel):
    """Imagen del dataset con su clase.

    Attributes:
        path: Ruta dentro del ZIP.
        label: Clase.
        source: Archivo en disco.
    """

    path: str
    label: str
    source: Path


class ClassCount(BaseModel):
    """Cantidad de imágenes de una clase.

    Attributes:
        label: Clase.
        images: Imágenes.
    """

    label: str
    images: int


class KaggleLicense(BaseModel):
    """Licencia en el formato de Kaggle.

    Attributes:
        name: Identificador de la licencia ("other" si se explica en la descripción).
    """

    name: str = "other"


class KaggleMetadata(BaseModel):
    """Contenido de `dataset-metadata.json`.

    Attributes:
        title: Título visible (6 a 50 caracteres).
        id: "usuario/identificador" del dataset en Kaggle.
        licenses: Licencias del dataset.
    """

    title: str = Field(min_length=6, max_length=50)
    id: str
    licenses: list[KaggleLicense] = [KaggleLicense()]


def collect(dataset: Path) -> list[LabeledImage]:
    """Lista las imágenes del dataset limpio, una subcarpeta por clase.

    Args:
        dataset: Carpeta generada por `clean_dataset.py`.

    Returns:
        Las imágenes en orden de clase y nombre.
    """
    images: list[LabeledImage] = []
    for folder in sorted(path for path in dataset.iterdir() if path.is_dir()):
        for file in sorted(folder.glob("*.jpg")):
            images.append(LabeledImage(path=f"images/{folder.name}/{file.name}", label=folder.name, source=file))
    return images


def dataset_card(counts: list[ClassCount]) -> str:
    """Escribe la ficha del dataset que Kaggle muestra como descripción.

    Args:
        counts: Imágenes por clase.

    Returns:
        El texto en Markdown.
    """
    total = sum(count.images for count in counts)
    rows = "\n".join(f"| {count.label} | {count.images} |" for count in counts)
    return f"""# {DEFAULT_TITLE}

Imágenes para entrenar un clasificador que detecte situaciones de riesgo en cámaras de seguridad.
Se usa en [AlertAI](https://github.com/CarlosIsaelRamirezGonzalez/AlertIA).

## Clases

| Clase | Imágenes |
|---|---|
{rows}
| **Total** | **{total}** |

"Normalidad" son negativos difíciles: escenas parecidas a las de riesgo que no lo son.

## Estructura

```
images/<clase>/<clase>-00001.jpg
labels.csv          # path,label
```

## Preparación

- Sin archivos dañados, truncados, de sistema ni de menos de 64 px de lado.
- Sin duplicados exactos ni casi duplicados (huella visual dHash, distancia ≤ 4).
- Las fotos que estaban en más de una clase se quitaron: su etiqueta es ambigua.
- JPEG RGB, orientación corregida, sin metadatos, lado más largo de 512 px.

## Cargarlo en Keras

```python
import keras

train, validation = keras.utils.image_dataset_from_directory(
    "images", image_size=(224, 224), batch_size=32,
    validation_split=0.2, subset="both", seed=42,
)
```

## Origen y licencia

TODO: indicar de dónde salieron las imágenes y con qué licencia se pueden usar. Si se tomaron de
internet, publica el dataset como privado hasta confirmarlo.
"""


def package(dataset: Path, output: Path, owner: str, slug: str) -> Path:
    """Crea la carpeta con el ZIP y los metadatos de Kaggle.

    Args:
        dataset: Carpeta del dataset limpio.
        output: Carpeta donde se deja el paquete.
        owner: Usuario de Kaggle.
        slug: Identificador del dataset en Kaggle.

    Returns:
        La ruta del ZIP.
    """
    images = collect(dataset)
    counts = [ClassCount(label=label, images=len(list(items))) for label, items in groupby(images, key=lambda image: image.label)]

    labels = io.StringIO()
    writer = csv.writer(labels)
    writer.writerow(["path", "label"])
    writer.writerows([image.path, image.label] for image in images)

    output.mkdir(parents=True, exist_ok=True)
    archive = output / "alertai-dataset.zip"
    # Los JPEG ya están comprimidos: guardarlos sin recomprimir es igual de pequeño y mucho más rápido.
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as bundle:
        bundle.writestr("README.md", dataset_card(counts), compress_type=zipfile.ZIP_DEFLATED)
        bundle.writestr("labels.csv", labels.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
        for image in images:
            bundle.write(image.source, image.path)

    metadata = KaggleMetadata(title=DEFAULT_TITLE, id=f"{owner}/{slug}")
    (output / "dataset-metadata.json").write_text(metadata.model_dump_json(indent=2), encoding="utf-8")
    return archive


def main() -> None:
    """Lee los argumentos y crea el paquete."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dataset", type=Path, help="Carpeta generada por clean_dataset.py")
    parser.add_argument("--output", type=Path, default=Path("AlertIA-kaggle"), help="Carpeta del paquete")
    parser.add_argument("--owner", default="TU_USUARIO_DE_KAGGLE", help="Tu usuario de Kaggle")
    parser.add_argument("--slug", default=DEFAULT_SLUG, help="Identificador del dataset en Kaggle")
    args = parser.parse_args()

    archive = package(args.dataset, args.output, args.owner, args.slug)
    size = archive.stat().st_size / 1024 / 1024
    print(f"Paquete listo: {archive} ({size:.1f} MB)")
    print(f"Metadatos: {args.output / 'dataset-metadata.json'}")


if __name__ == "__main__":
    main()
