"""Cámaras del usuario y su monitoreo con la IA."""

from flask import Blueprint

home = Blueprint('home', __name__)

# Las vistas se importan al final porque usan el blueprint de arriba.
from . import views  # noqa: E402,F401
