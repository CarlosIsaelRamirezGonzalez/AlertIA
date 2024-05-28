from flask import Blueprint

alert = Blueprint('alert', __name__)

from . import views