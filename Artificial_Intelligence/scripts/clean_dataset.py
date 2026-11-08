"""Limpia y normaliza el dataset de imágenes antes de entrenar.

Nunca modifica ni borra la carpeta original. Revisa cada archivo y escribe un dataset nuevo y
limpio en otra carpeta, más un reporte de todo lo que se descartó y por qué:

- Basura del sistema (`.DS_Store`, `._*`, `desktop.ini`, `Thumbs.db`) y archivos que no son imágenes.
- Imágenes dañadas, truncadas o en un formato que no se puede leer.
- Imágenes demasiado pequeñas para aprender algo de ellas.
- Duplicados exactos y casi duplicados (la misma foto recortada, comprimida o en otro formato).
  Si una misma foto aparece en dos clases distintas, no se queda en ninguna: hay que revisarla.

Las que pasan se guardan como JPEG RGB, con la orientación corregida, sin metadatos y con el lado
más largo limitado (por defecto 512 px), con nombres ASCII consecutivos por clase.

Uso:
    python clean_dataset.py ORIGEN                    # solo reporte, no escribe imágenes
    python clean_dataset.py ORIGEN --output DESTINO   # escribe el dataset limpio
"""

import argparse
import hashlib
import io
import os
import random
import re
import sys
import unicodedata
from concurrent.futures import ProcessPoolExecutor
from itertools import groupby
from pathlib import Path
from typing import Literal

from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel, Field

# Una imagen truncada no debe colarse como válida.
Image.MAX_IMAGE_PIXELS = 80_000_000

IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".jgp", ".png", ".webp", ".avif", ".bmp", ".gif", ".tif", ".tiff"})
SYSTEM_JUNK = re.compile(r"^(\.ds_store|\._.*|desktop\.ini|thumbs\.db|\.localized)$", re.IGNORECASE)

IssueReason = Literal[
    "basura-del-sistema",
    "no-es-imagen",
    "danada",
    "muy-pequena",
    "duplicada",
    "casi-duplicada",
    "conflicto-entre-clases",
    "clase-excluida",
]


class ClassAlias(BaseModel):
    """Nombre de carpeta que se convierte en una clase del modelo.

    Attributes:
        folder: Nombre de la carpeta en el dataset original.
        label: Nombre de la clase en el dataset limpio.
    """

    folder: str
    label: str


# Las carpetas en plural se unifican con los nombres que ya usa el modelo (`app/detection.py`).
# Las que no aparecen aquí conservan su nombre, limpio.
CLASS_ALIASES = (
    ClassAlias(folder="Armas blancas", label="Arma blanca"),
    ClassAlias(folder="Armas cortas", label="Arma corta"),
    ClassAlias(folder="Armas largas", label="Arma larga"),
    ClassAlias(folder="Ataque de perros", label="Ataque de perro"),
    ClassAlias(folder="Encañonamiento", label="Encañonamiento"),
    ClassAlias(folder="Golpes", label="Golpe"),
    ClassAlias(folder="Incendios", label="Incendio"),
    ClassAlias(folder="Negativos dificiles", label="Normalidad"),
    ClassAlias(folder="Patadas", label="Patada"),
    ClassAlias(folder="Personas heridas", label="Persona herida"),
)

# Carpetas que no son una clase; se pueden incluir con --include.
DEFAULT_EXCLUDED = ("Carpeta general",)


class Settings(BaseModel):
    """Opciones de la limpieza.

    Attributes:
        source: Carpeta original, con una subcarpeta por clase.
        output: Carpeta del dataset limpio; sin ella solo se genera el reporte.
        max_side: Lado más largo de las imágenes guardadas, en píxeles.
        min_side: Lado más corto mínimo para aceptar una imagen.
        quality: Calidad JPEG de las imágenes guardadas.
        near_distance: Diferencia máxima entre huellas para considerar dos fotos casi iguales.
        excluded: Carpetas que no se usan como clase.
        workers: Procesos en paralelo.
    """

    source: Path
    output: Path | None = None
    max_side: int = Field(default=512, ge=64)
    min_side: int = Field(default=64, ge=1)
    quality: int = Field(default=90, ge=50, le=100)
    near_distance: int = Field(default=4, ge=0, le=16)
    excluded: tuple[str, ...] = DEFAULT_EXCLUDED
    workers: int = Field(default=max(1, (os.cpu_count() or 2) - 1), ge=1)


class ImageCheck(BaseModel):
    """Resultado de revisar un archivo.

    Attributes:
        path: Ruta del archivo original.
        label: Clase a la que pertenece.
        ok: Si se pudo leer como imagen válida.
        problem: Qué le pasa, si no es válida.
        detail: Mensaje del error, si hubo.
        width: Ancho en píxeles.
        height: Alto en píxeles.
        file_hash: Huella del archivo completo, para duplicados exactos.
        visual_hash: Huella visual de 64 bits, para casi duplicados.
    """

    path: Path
    label: str
    ok: bool
    problem: IssueReason | None = None
    detail: str = ""
    width: int = 0
    height: int = 0
    file_hash: str = ""
    visual_hash: int = 0


class FileIssue(BaseModel):
    """Archivo que no pasa al dataset limpio.

    Attributes:
        path: Ruta del archivo original.
        reason: Motivo.
        detail: Información adicional (por ejemplo, con qué archivo se repite).
    """

    path: str
    reason: IssueReason
    detail: str = ""


class ClassSummary(BaseModel):
    """Conteo de una clase.

    Attributes:
        folder: Carpeta original.
        label: Nombre de la clase en el dataset limpio.
        found: Archivos encontrados.
        kept: Imágenes que pasan.
    """

    folder: str
    label: str
    found: int
    kept: int = 0


class CleanReport(BaseModel):
    """Reporte completo de la limpieza.

    Attributes:
        source: Carpeta original.
        output: Carpeta del dataset limpio, si se escribió.
        source_bytes: Tamaño de las imágenes originales que pasan.
        estimated_bytes: Tamaño estimado del dataset limpio, a partir de una muestra.
        written_bytes: Tamaño real del dataset limpio, si se escribió.
        classes: Conteo por clase.
        issues: Archivos descartados.
    """

    source: str
    output: str | None
    source_bytes: int = 0
    estimated_bytes: int = 0
    written_bytes: int = 0
    classes: list[ClassSummary] = []
    issues: list[FileIssue] = []


class WriteJob(BaseModel):
    """Imagen que se va a guardar en el dataset limpio.

    Attributes:
        source: Archivo original.
        target: Archivo de destino.
        max_side: Lado más largo permitido.
        quality: Calidad JPEG.
    """

    source: Path
    target: Path
    max_side: int
    quality: int


# ---------------------------------------------------------------------------
# Clases
# ---------------------------------------------------------------------------


def ascii_key(name: str) -> str:
    """Reduce un nombre a letras ASCII, para reconocer carpetas aunque tengan acentos dañados.

    Un ZIP descomprimido con otra codificación puede convertir "ñ" en otro carácter; quitando
    todo lo que no sea a-z, "Encañonamiento" y su versión dañada dan la misma clave.

    Args:
        name: Nombre de la carpeta.

    Returns:
        Solo las letras a-z del nombre, en minúsculas.
    """
    return re.sub(r"[^a-z]", "", name.lower())


def label_for(folder: str) -> str:
    """Nombre de clase para una carpeta del dataset original.

    Args:
        folder: Nombre de la carpeta.

    Returns:
        El nombre de la clase en el dataset limpio.
    """
    key = ascii_key(folder)
    for alias in CLASS_ALIASES:
        if ascii_key(alias.folder) == key:
            return alias.label
    return unicodedata.normalize("NFC", folder).strip()


def slug(label: str) -> str:
    """Convierte una clase en un prefijo de archivo ASCII.

    Args:
        label: Nombre de la clase.

    Returns:
        El nombre sin acentos, en minúsculas y con guiones.
    """
    plain = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


# ---------------------------------------------------------------------------
# Revisión de cada archivo (corre en paralelo)
# ---------------------------------------------------------------------------


def visual_hash(image: Image.Image) -> int:
    """Huella visual de 64 bits (dHash): compara cada píxel con su vecino en una miniatura gris.

    Dos fotos iguales con distinta compresión, tamaño o formato dan huellas casi idénticas.

    Args:
        image: Imagen ya cargada.

    Returns:
        La huella como entero de 64 bits.
    """
    small = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    pixels = small.tobytes()
    bits = 0
    for row in range(8):
        for column in range(8):
            left = pixels[row * 9 + column]
            right = pixels[row * 9 + column + 1]
            bits = (bits << 1) | (left > right)
    return bits


def inspect(path: Path, label: str, min_side: int) -> ImageCheck:
    """Abre un archivo y comprueba que sea una imagen completa y utilizable.

    Args:
        path: Archivo que se revisa.
        label: Clase a la que pertenece.
        min_side: Lado más corto mínimo aceptado.

    Returns:
        El resultado de la revisión.
    """
    if SYSTEM_JUNK.match(path.name):
        return ImageCheck(path=path, label=label, ok=False, problem="basura-del-sistema")
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        return ImageCheck(path=path, label=label, ok=False, problem="no-es-imagen", detail=path.suffix)

    data = path.read_bytes()
    try:
        # verify() detecta archivos corruptos; load() detecta los truncados.
        with Image.open(io.BytesIO(data)) as probe:
            probe.verify()
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            image = ImageOps.exif_transpose(image)
            width, height = image.size
            fingerprint = visual_hash(image)
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, Image.DecompressionBombError) as error:
        return ImageCheck(path=path, label=label, ok=False, problem="danada", detail=str(error)[:160])

    if min(width, height) < min_side:
        return ImageCheck(path=path, label=label, ok=False, problem="muy-pequena", detail=f"{width}×{height}", width=width, height=height)
    return ImageCheck(
        path=path,
        label=label,
        ok=True,
        width=width,
        height=height,
        file_hash=hashlib.sha256(data).hexdigest(),
        visual_hash=fingerprint,
    )


def normalized_jpeg(path: Path, max_side: int, quality: int) -> bytes:
    """Convierte una imagen al formato del dataset limpio.

    Args:
        path: Archivo original.
        max_side: Lado más largo permitido.
        quality: Calidad JPEG.

    Returns:
        La imagen como JPEG RGB, orientada, reducida y sin metadatos.
    """
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode in ("RGBA", "LA", "P"):
            # La transparencia se aplana sobre blanco, no sobre negro.
            image = image.convert("RGBA")
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=quality, optimize=True, progressive=True)
        return buffer.getvalue()


def inspect_job(job: tuple[Path, str, int]) -> ImageCheck:
    """Adaptador para el grupo de procesos.

    Args:
        job: Archivo, clase y lado mínimo.

    Returns:
        El resultado de la revisión.
    """
    return inspect(*job)


def write_job(job: WriteJob) -> int:
    """Guarda una imagen en el dataset limpio.

    Args:
        job: Qué imagen y a dónde.

    Returns:
        Bytes escritos.
    """
    data = normalized_jpeg(job.source, job.max_side, job.quality)
    job.target.write_bytes(data)
    return len(data)


def size_job(job: WriteJob) -> int:
    """Calcula cuánto pesaría una imagen normalizada, sin escribirla.

    Args:
        job: Qué imagen.

    Returns:
        Bytes que ocuparía.
    """
    return len(normalized_jpeg(job.source, job.max_side, job.quality))


# ---------------------------------------------------------------------------
# Limpieza completa
# ---------------------------------------------------------------------------


def hamming(left: int, right: int) -> int:
    """Cuántos bits difieren entre dos huellas.

    Args:
        left: Primera huella.
        right: Segunda huella.

    Returns:
        La distancia de Hamming.
    """
    return (left ^ right).bit_count()


def find_duplicates(checks: list[ImageCheck], near_distance: int) -> list[FileIssue]:
    """Marca duplicados exactos, casi duplicados y fotos repetidas entre clases.

    De cada grupo se queda la imagen de mayor resolución. Si el grupo mezcla clases, se
    descartan todas, porque no se sabe cuál etiqueta es la correcta.

    Args:
        checks: Imágenes válidas.
        near_distance: Diferencia máxima entre huellas para considerarlas casi iguales.

    Returns:
        Las imágenes que no deben pasar.
    """
    # Grupos por unión de conjuntos: exactos por archivo, casi iguales por huella visual.
    parent = list(range(len(checks)))

    def root(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def join(left: int, right: int) -> None:
        parent[root(left)] = root(right)

    def clusters(key) -> list[list[int]]:
        """Agrupa los índices que comparten una clave, ordenándolos por ella."""
        ordered = sorted(range(len(checks)), key=key)
        return [list(members) for _, members in groupby(ordered, key=key)]

    # Duplicados exactos: mismo contenido de archivo.
    for members in clusters(lambda index: checks[index].file_hash):
        for index in members[1:]:
            join(index, members[0])

    # Casi duplicados: se comparan solo imágenes que comparten un bloque de 16 bits de la huella.
    if near_distance > 0:
        for shift in (0, 16, 32, 48):
            for members in clusters(lambda index: (checks[index].visual_hash >> shift) & 0xFFFF):
                if len(members) > 60:
                    # Un bloque tan común (por ejemplo, imágenes casi lisas) da falsos positivos.
                    continue
                for position, left in enumerate(members):
                    for right in members[position + 1 :]:
                        if hamming(checks[left].visual_hash, checks[right].visual_hash) <= near_distance:
                            join(left, right)

    issues: list[FileIssue] = []
    for members in clusters(root):
        if len(members) == 1:
            continue
        labels = {checks[index].label for index in members}
        names = ", ".join(str(checks[index].path) for index in members)
        if len(labels) > 1:
            issues += [
                FileIssue(path=str(checks[index].path), reason="conflicto-entre-clases", detail=f"misma foto en: {names}")
                for index in members
            ]
            continue
        best = max(members, key=lambda index: checks[index].width * checks[index].height)
        for index in members:
            if index == best:
                continue
            exact = checks[index].file_hash == checks[best].file_hash
            issues.append(
                FileIssue(
                    path=str(checks[index].path),
                    reason="duplicada" if exact else "casi-duplicada",
                    detail=f"se queda {checks[best].path}",
                )
            )
    return issues


def human(size: int) -> str:
    """Formatea un tamaño en bytes.

    Args:
        size: Bytes.

    Returns:
        El tamaño legible, por ejemplo "1.6 GB".
    """
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GB"


def clean(settings: Settings) -> CleanReport:
    """Revisa todo el dataset y, si hay carpeta de salida, escribe la versión limpia.

    Args:
        settings: Opciones de la limpieza.

    Returns:
        El reporte.
    """
    report = CleanReport(source=str(settings.source), output=str(settings.output) if settings.output else None)
    excluded = {ascii_key(name) for name in settings.excluded}

    # Archivos por clase.
    jobs: list[tuple[Path, str, int]] = []
    for folder in sorted(path for path in settings.source.iterdir() if path.is_dir()):
        label = label_for(folder.name)
        files = sorted(path for path in folder.rglob("*") if path.is_file())
        if ascii_key(folder.name) in excluded:
            report.issues += [FileIssue(path=str(path), reason="clase-excluida", detail=folder.name) for path in files]
            continue
        report.classes.append(ClassSummary(folder=folder.name, label=label, found=len(files)))
        jobs += [(path, label, settings.min_side) for path in files]
    for path in settings.source.iterdir():
        if path.is_file():
            report.issues.append(FileIssue(path=str(path), reason="basura-del-sistema" if SYSTEM_JUNK.match(path.name) else "no-es-imagen"))

    print(f"Revisando {len(jobs)} archivos con {settings.workers} procesos…", flush=True)
    with ProcessPoolExecutor(settings.workers) as pool:
        checks = list(pool.map(inspect_job, jobs, chunksize=32))

    valid = [check for check in checks if check.ok]
    report.issues += [
        FileIssue(path=str(check.path), reason=check.problem or "danada", detail=check.detail) for check in checks if not check.ok
    ]
    duplicates = find_duplicates(valid, settings.near_distance)
    report.issues += duplicates
    dropped = {issue.path for issue in duplicates}
    kept = [check for check in valid if str(check.path) not in dropped]
    report.source_bytes = sum(check.path.stat().st_size for check in kept)

    for summary in report.classes:
        summary.kept = sum(1 for check in kept if check.label == summary.label)

    # Plan de escritura: nombres ASCII consecutivos por clase.
    plan: list[WriteJob] = []
    target_root = settings.output or Path("_sin_salida")
    for label, members in groupby(sorted(kept, key=lambda check: check.label), key=lambda check: check.label):
        for number, check in enumerate(members, start=1):
            target = target_root / label / f"{slug(label)}-{number:05d}.jpg"
            plan.append(WriteJob(source=check.path, target=target, max_side=settings.max_side, quality=settings.quality))

    if settings.output is None:
        # Sin salida: se estima el tamaño final con una muestra.
        sample = random.Random(7).sample(plan, min(200, len(plan)))
        with ProcessPoolExecutor(settings.workers) as pool:
            sample_bytes = sum(pool.map(size_job, sample, chunksize=8))
        report.estimated_bytes = int(sample_bytes / max(1, len(sample)) * len(plan))
        return report

    if settings.output.exists() and any(settings.output.iterdir()):
        sys.exit(f"La carpeta de salida {settings.output} ya existe y no está vacía; elige otra o bórrala tú.")
    for label in {job.target.parent for job in plan}:
        label.mkdir(parents=True, exist_ok=True)
    print(f"Escribiendo {len(plan)} imágenes en {settings.output}…", flush=True)
    with ProcessPoolExecutor(settings.workers) as pool:
        report.written_bytes = sum(pool.map(write_job, plan, chunksize=16))
    return report


def print_summary(report: CleanReport) -> None:
    """Muestra el resultado en la terminal.

    Args:
        report: Reporte de la limpieza.
    """
    print("\nClases:")
    for summary in report.classes:
        renamed = f" → {summary.label}" if summary.label != summary.folder else ""
        print(f"  {summary.folder}{renamed}: {summary.kept} de {summary.found}")

    print("\nDescartados:")
    reasons = [(reason, len(list(items))) for reason, items in groupby(sorted(issue.reason for issue in report.issues))]
    for reason, count in sorted(reasons, key=lambda item: -item[1]):
        print(f"  {reason}: {count}")

    kept = sum(summary.kept for summary in report.classes)
    print(f"\nImágenes que pasan: {kept}")
    print(f"Peso original de esas imágenes: {human(report.source_bytes)}")
    if report.written_bytes:
        print(f"Peso del dataset limpio: {human(report.written_bytes)}")
    elif report.estimated_bytes:
        print(f"Peso estimado del dataset limpio: {human(report.estimated_bytes)}")


def main() -> None:
    """Lee los argumentos, limpia y guarda el reporte."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="Carpeta original, con una subcarpeta por clase")
    parser.add_argument("--output", type=Path, help="Carpeta nueva para el dataset limpio (sin ella, solo reporte)")
    parser.add_argument("--max-side", type=int, default=512, help="Lado más largo al guardar (por defecto 512)")
    parser.add_argument("--min-side", type=int, default=64, help="Lado más corto mínimo (por defecto 64)")
    parser.add_argument("--near-distance", type=int, default=4, help="Tolerancia para casi duplicados; 0 la desactiva")
    parser.add_argument("--include", action="append", default=[], help="Usar como clase una carpeta excluida por defecto")
    parser.add_argument("--report", type=Path, help="Dónde guardar el reporte JSON")
    args = parser.parse_args()

    settings = Settings(
        source=args.source,
        output=args.output,
        max_side=args.max_side,
        min_side=args.min_side,
        near_distance=args.near_distance,
        excluded=tuple(name for name in DEFAULT_EXCLUDED if ascii_key(name) not in {ascii_key(item) for item in args.include}),
    )
    report = clean(settings)
    print_summary(report)

    report_path = args.report or (
        settings.output.with_name(f"{settings.output.name}-reporte.json") if settings.output else Path("reporte-limpieza.json")
    )
    report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    print(f"\nReporte completo: {report_path}")


if __name__ == "__main__":
    main()
