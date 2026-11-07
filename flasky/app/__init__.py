"""Crea la aplicación de Flask con sus extensiones y sus secciones (blueprints)."""

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask_wtf.csrf import generate_csrf

from config import get_config

# Extensiones; se conectan a la aplicación dentro de create_app.
bootstrap = Bootstrap()
db = MongoEngine()
login_manager = LoginManager()
mail = Mail()

# A dónde se manda a quien entra a una página protegida sin sesión, y qué se le dice.
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please log in before accesing this page."


def format_date(value):
    """Da formato a una fecha para mostrarla, como `07-11-2026 15:21`.

    Args:
        value: Fecha; las notificaciones viejas pueden traerla como texto.

    Returns:
        El texto de la fecha, o el valor tal cual si no es una fecha.
    """
    return value.strftime('%d-%m-%Y %H:%M') if hasattr(value, 'strftime') else value


def create_app(config_name):
    """Arma la aplicación para un entorno.

    Args:
        config_name: `development`, `testing`, `production` o `default`.

    Returns:
        La aplicación de Flask lista para correr.
    """
    app = Flask(__name__)
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Conecta las extensiones.
    config_class.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # Disponibles en todas las plantillas: el token de los botones de borrar y el formato de fecha.
    app.jinja_env.globals['csrf_token'] = generate_csrf
    app.jinja_env.filters['fecha'] = format_date

    # Registra cada sección con su prefijo de ruta.
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .alert import alert as alert_blueprint
    from .home import home as home_blueprint
    from .admin import admin as admin_blueprint
    from .help import help as help_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(alert_blueprint, url_prefix="/alert")
    app.register_blueprint(home_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(help_blueprint, url_prefix='/help')

    return app
