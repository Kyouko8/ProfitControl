from flask import Blueprint

payment_bp = Blueprint("payment", __name__, template_folder="templates", url_prefix="/payment")


from . import routes