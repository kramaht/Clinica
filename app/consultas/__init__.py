from flask import Blueprint
consultas = Blueprint('consultas', __name__)
from . import routes
