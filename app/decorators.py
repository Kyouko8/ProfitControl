from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

from .models import Profile


def profile_active_required(f):
    @wraps(f)
    def verify(*args, **kwargs):
        if not Profile.get_count_by_user(current_user.id, only_active=True):
            flash("Se requiere algún perfil activo para ingresar a esta sección.")
            return redirect(url_for("admin.profile_list"))

        return f(*args, **kwargs)

    return verify