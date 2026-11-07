"""Ayuda y reporte de problemas."""

from flask import Blueprint

help = Blueprint('help', __name__)

# Las vistas se importan al final porque usan el blueprint de arriba.
from . import views  # noqa: E402,F401
