from flask import Blueprint
pacientes = Blueprint('pacientes', __name__)
from . import routes
