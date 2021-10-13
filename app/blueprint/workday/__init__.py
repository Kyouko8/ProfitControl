from flask import Blueprint

name = "workday"
workday_bp = Blueprint(name, __name__, template_folder="templates", url_prefix=f'/{name}')

from . import routes
