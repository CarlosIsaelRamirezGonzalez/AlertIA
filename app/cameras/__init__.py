from flask import Blueprint

cameras = Blueprint('cameras', __name__)

from . import views