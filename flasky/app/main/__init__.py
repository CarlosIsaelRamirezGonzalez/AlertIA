"""Página pública de presentación."""

from flask import Blueprint

main = Blueprint('main', __name__)

# Las vistas se importan al final porque usan el blueprint de arriba.
from . import views  # noqa: E402,F401
