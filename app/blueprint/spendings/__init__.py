from flask import Blueprint

name = "spending"
spending_bp = Blueprint(name, __name__, template_folder="templates", url_prefix=f'/workday/{name}')

from . import routes
