"""Modelos Pydantic de la aplicación: reemplazan a los diccionarios en todo el código.

Si una librería exige un diccionario, el modelo se convierte con `model_dump()` solo en ese punto.
La conexión a MongoDB (`MongoSettings`) está en config.py, para no crear un ciclo de importación.
"""

from threading import Thread

from pydantic import BaseModel, ConfigDict


class EmailAttachment(BaseModel):
    """Archivo adjunto de un correo.

    Attributes:
        filename: Nombre con el que llega el archivo.
        content_type: Tipo de contenido, como `image/png`.
        data: Contenido del archivo.
    """

    model_config = ConfigDict(frozen=True)

    filename: str
    content_type: str
    data: bytes


class CameraDevice(BaseModel):
    """Cámara conectada a esta computadora, para elegirla al registrar una cámara.

    Attributes:
        device_id: Identificador: el número de OpenCV o el identificador de Windows.
        name: Nombre que se muestra en la lista.
    """

    model_config = ConfigDict(frozen=True)

    device_id: str
    name: str


class LoginTip(BaseModel):
    """Dato curioso que se muestra en la pantalla de inicio de sesión.

    Attributes:
        text: Texto del dato.
        icon: Clases de Font Awesome del icono.
    """

    model_config = ConfigDict(frozen=True)

    text: str
    icon: str


class PlaceAlerts(BaseModel):
    """Alertas que se activan solas según el lugar de la cámara.

    Attributes:
        place: Lugar, como `Home` o `Street`.
        alerts: Alertas que le corresponden.
    """

    model_config = ConfigDict(frozen=True)

    place: str
    alerts: tuple[str, ...]


class MonitoredCamera(BaseModel):
    """Cámara que se está vigilando en esta computadora.

    Attributes:
        camera_id: Identificador de la cámara en MongoDB.
        thread: Hilo que la vigila.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    camera_id: str
    thread: Thread


class ApiMessage(BaseModel):
    """Respuesta JSON de una acción.

    Attributes:
        message: Mensaje de éxito.
        error: Mensaje de error.
        details: Detalle técnico del error.
    """

    message: str | None = None
    error: str | None = None
    details: str | None = None
