"""Notificaciones de amenazas detectadas."""

from flask import Blueprint

alert = Blueprint('alert', __name__)

# Las vistas se importan al final porque usan el blueprint de arriba.
from . import views  # noqa: E402,F401
