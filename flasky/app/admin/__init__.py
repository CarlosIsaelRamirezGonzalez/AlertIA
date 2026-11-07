"""Panel del administrador."""

from flask import Blueprint

admin = Blueprint('admin', __name__)

# Las vistas se importan al final porque usan el blueprint de arriba.
from . import views  # noqa: E402,F401
