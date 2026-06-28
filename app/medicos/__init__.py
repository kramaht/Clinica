from flask import Blueprint
medicos = Blueprint('medicos', __name__)
from . import routes
