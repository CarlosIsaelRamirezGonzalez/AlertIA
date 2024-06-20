from flask import Blueprint

help = Blueprint('help', __name__)

from . import views