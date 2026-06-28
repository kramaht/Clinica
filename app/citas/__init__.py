from flask import Blueprint
citas = Blueprint('citas', __name__)
from . import routes
