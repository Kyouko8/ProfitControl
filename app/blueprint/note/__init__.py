from flask import Blueprint

name = "note"
note_bp = Blueprint(name, __name__, template_folder="templates", url_prefix=f'/{name}s')

from . import routes
