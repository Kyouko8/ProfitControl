from flask import Blueprint

name = "profile"
profile_bp = Blueprint(name, __name__, template_folder="templates", url_prefix=f'/{name}')

from . import routes
