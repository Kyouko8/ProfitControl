from flask import Blueprint

name = "shopping_spending"
s_spending_bp = Blueprint(name, __name__, template_folder="templates", url_prefix=f'/shopping/spendings')

from . import routes
