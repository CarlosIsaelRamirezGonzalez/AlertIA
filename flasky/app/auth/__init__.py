"""Cuentas: registro, inicio de sesión, confirmación y contraseña."""

from flask import Blueprint

auth = Blueprint('auth', __name__)

# Las vistas se importan al final porque usan el blueprint de arriba.
from . import views  # noqa: E402,F401
