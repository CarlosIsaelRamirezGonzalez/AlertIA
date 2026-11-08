"""Configuración de AlertAI, leída de variables de entorno (ver `.env.example`)."""

import os

from pydantic import BaseModel, ConfigDict

# Conexión a MongoDB. Antes se usaron STRING_CONNECTION y MONGODB_SETTINGS; se siguen aceptando.
MONGODB_URI = (
    os.environ.get('MONGODB_URI')
    or os.environ.get('STRING_CONNECTION')
    or os.environ.get('MONGODB_SETTINGS')
    or 'localhost'
)
DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'Artificial_Intelligence', 'Aria.keras')
TEN_DAYS_SECONDS = 10 * 24 * 3600
# Solo para desarrollo local: cualquiera puede leerla en el código, así que nunca protege nada real.
DEVELOPMENT_SECRET_KEY = 'solo-para-desarrollo-local'


class MongoSettings(BaseModel):
    """Conexión a MongoDB que espera Flask-MongoEngine.

    Vive aquí y no en app/schemas.py porque app importa este archivo al arrancar.

    Attributes:
        host: Dirección o cadena de conexión.
        db: Nombre de la base de datos.
        port: Puerto; se ignora si `host` es una cadena `mongodb+srv://`.
    """

    model_config = ConfigDict(frozen=True)

    host: str
    db: str
    port: int = 27017


def mongo_settings(database: str) -> MongoSettings:
    """Arma la conexión a MongoDB para una base de datos.

    Args:
        database: Nombre de la base.

    Returns:
        La configuración de la conexión.
    """
    return MongoSettings(host=MONGODB_URI, db=database)


class Config:
    """Configuración común a todos los entornos."""

    # Antes se usó SECRET; se sigue aceptando. Fuera de desarrollo es obligatoria.
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('SECRET')
    REMEMBER_COOKIE_DURATION = int(os.environ.get('REMEMBER_COOKIE_DURATION', TEN_DAYS_SECONDS))

    # Correo
    MAIL_SERVER = os.environ.get('EMAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', 'on', '1')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[AlertAI]'
    FLASKY_MAIL_SENDER = 'AlertAI Admin <alertia2023@gmail.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'alertia2023@gmail.com')

    # Dirección pública de la app, para los enlaces de los correos.
    BASE_URL = os.environ.get('ALERTAI_BASE_URL', 'http://127.0.0.1:5000').rstrip('/')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    MODEL_PATH = os.environ.get('ALERTAI_MODEL_PATH', DEFAULT_MODEL_PATH)

    @staticmethod
    def init_app(app):
        """Revisa la configuración antes de arrancar.

        Args:
            app: Aplicación de Flask.

        Raises:
            RuntimeError: Si falta `SECRET_KEY`: sin ella, cualquiera podría falsificar sesiones.
        """
        if not app.config.get('SECRET_KEY'):
            raise RuntimeError('Falta SECRET_KEY. Defínela en el entorno o en flasky/.env (ver .env.example).')


class DevelopmentConfig(Config):
    """Desarrollo: modo de depuración y base `development_db`."""

    DEBUG = True
    # En desarrollo se puede arrancar sin definirla; en pruebas y producción no.
    SECRET_KEY = Config.SECRET_KEY or DEVELOPMENT_SECRET_KEY
    # Flask-MongoEngine exige un diccionario: se convierte solo en este punto.
    MONGODB_SETTINGS = mongo_settings('development_db').model_dump()


class TestingConfig(Config):
    """Pruebas: base `testing_db`."""

    TESTING = True
    MONGODB_SETTINGS = mongo_settings('testing_db').model_dump()


class ProductionConfig(Config):
    """Producción: base `production_db`."""

    MONGODB_SETTINGS = mongo_settings('production_db').model_dump()


# Entornos disponibles; `default` es el que se usa si no se indica ninguno.
CONFIGS = (
    ('development', DevelopmentConfig),
    ('testing', TestingConfig),
    ('production', ProductionConfig),
    ('default', DevelopmentConfig),
)


def get_config(name: str) -> type[Config]:
    """Busca la configuración de un entorno.

    Args:
        name: `development`, `testing`, `production` o `default`.

    Returns:
        La clase de configuración.

    Raises:
        KeyError: Si el entorno no existe.
    """
    for config_name, config_class in CONFIGS:
        if config_name == name:
            return config_class
    raise KeyError(f"Unknown configuration: {name}")
