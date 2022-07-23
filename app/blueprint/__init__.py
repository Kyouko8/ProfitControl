from .note import note_bp
from .client import client_bp
from .product import product_bp
from .profile import profile_bp
from .shopping_spendings import s_spending_bp
from .shoppingday import shoppingday_bp
from .spendings import spending_bp
from .workday import workday_bp


BLUEPRINTS = [note_bp, client_bp, product_bp, profile_bp, s_spending_bp, shoppingday_bp, spending_bp, workday_bp]

from app.utils.auth import suscription_required


@note_bp.before_request
@suscription_required
def before_request():
    pass

@client_bp.before_request
@suscription_required
def before_request():
    pass

@product_bp.before_request
@suscription_required
def before_request():
    pass

@profile_bp.before_request
@suscription_required
def before_request():
    pass

@s_spending_bp.before_request
@suscription_required
def before_request():
    pass

@shoppingday_bp.before_request
@suscription_required
def before_request():
    pass

@spending_bp.before_request
@suscription_required
def before_request():
    pass

@workday_bp.before_request
@suscription_required
def before_request():
    pass


