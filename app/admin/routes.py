"""Admin routes"""
import logging
from flask import render_template, url_for, redirect, flash
from flask_login import login_required, logout_user, current_user

from app.auth.models import User

from app.utils.auth import suscription_required

from . import admin_bp
from .forms import ChangeEmailUserForm, ChangeNameUserForm, ChangePasswordUserForm

logger = logging.getLogger(__name__)


@admin_bp.route("/")
@admin_bp.route("/user")
@login_required
def index():
    return redirect(url_for("admin.user_details"))

@admin_bp.route("/user/details/")
@login_required
def user_details():
    return render_template("admin/user/details.html")

@admin_bp.route("/settings/")
@admin_bp.route("user/settings/")
def user_settings():
    return render_template("admin/user/settings.html")

@admin_bp.route("/user/edit/", methods=["get", "post"])
@login_required
def user_edit():
    form = ChangeNameUserForm()

    if form.validate_on_submit():
        name = (form.name.data)

        if len(name) > 3:
            user = current_user
            user.username = name
            user.save()

            return redirect(url_for("admin.user_details"))
    else:
        form.name.data = current_user.username

    return render_template("admin/user/edit.html", form=form)


@admin_bp.route("/user/change-password/", methods=["get", "post"])
@login_required
def user_change_password():
    form = ChangePasswordUserForm()

    if form.validate_on_submit():
        current_email = (form.current_email.data).lower()
        current_password = (form.current_password.data)
        password = form.password.data
        password_confirm = form.confirm.data

        if (password != password_confirm):
            form.password.errors.append("Las contraseñas no coinciden.")

        elif (password == current_password):
            form.password.errors.append("La contraseña ingresada es igual a la actual.")
            
        elif len(password) >= 8:
            user = current_user
            if user.email.lower() == current_email.lower():
                if user.check_password(current_password):
                    user.set_password(password)
                    user.save()
                    logout_user()
                    flash("Contraseña actualizada. Inicie sesión nuevamente para continuar.")
                    return redirect(url_for("auth.login", next=url_for("admin.user_details")))

                else:
                    form.current_password.errors.append("Contraseña incorrecta.")
            else:
                form.current_email.errors.append("Correo electrónico incorrecto.")
                form.current_email.errors.append("Ingrese correo electrónico registrado en esta cuenta.")
        else:
            form.password.errors.append("Contraseña muy corta. Mínimo 8 caracteres.")

    return render_template("admin/user/change_password.html", form=form)

 
@admin_bp.route("/user/change-email/", methods=["get", "post"])
@login_required
def user_change_email():
    form = ChangeEmailUserForm()

    if form.validate_on_submit():
        current_email = (form.current_email.data).lower()
        current_password = (form.current_password.data)
        email = form.email.data

        user = current_user
        if current_email.lower() == email.lower():
            form.email.errors.append("Los correos electrónicos son iguales.")

        elif user.email.lower() == current_email.lower():
            if user.check_password(current_password):
                if not User.get_by_email(email):
                    user.email = email.lower()
                    user.save()
                    logout_user()
                    flash("Correo electrónico actualizado. Inicie sesión nuevamente para continuar.")
                    
                    return redirect(url_for("auth.login", next=url_for("admin.user_details")))
                else:
                    form.email.errors.append("El correo electrónico ingresado ya existe en otra cuenta.")

            else:
                form.current_password.errors.append("Contraseña incorrecta.")
        else:
            form.current_email.errors.append("Correo electrónico incorrecto.")
            form.current_email.errors.append("Ingrese correo electrónico registrado en esta cuenta.")
        

    return render_template("admin/user/change_email.html", form=form)
   