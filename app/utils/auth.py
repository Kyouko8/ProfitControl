from functools import wraps


from flask import redirect, url_for
from flask_login import current_user

def suscription_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('public.login'))

        if not current_user.suscription_active:
            return redirect(url_for('payment.manage_suscription'))

        return func(*args, **kwargs)

    return decorated_view