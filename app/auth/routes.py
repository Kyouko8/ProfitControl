"""Auth routes"""
import datetime
import json
import logging

from app import login_manager
from app.models.models import Profile
from flask import (flash, make_response, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user

from . import auth_bp
from .forms import LoginForm, SignupForm
from .models import User

logger = logging.getLogger(__name__)

def _get_user_list(cookie_list):
    user_list = []
    for token in tuple(cookie_list):
        _user = User.get_by_token(token)
        can_log_fast = None if not _user else _user.get_config_force("can_log_fast", 1).as_int()
        if not can_log_fast:
            cookie_list.remove(token)
            continue

        if not _user in user_list:
            user_list.append(_user)

    return user_list, cookie_list


@auth_bp.route("/auth/index.html")
def index():
    return render_template("auth/index.html")


@auth_bp.route("/auth/login/", methods=["GET", "POST"])
@auth_bp.route("/auth/login/<user_token>/", methods=["GET", "POST"])
def login(user_token=None):
    if current_user.is_authenticated:
        flash("Ya tienes una sesión iniciada.", "error")
        return redirect(url_for("public.home"))

    form = LoginForm()

    # Cookie Manager
    user_data = None
    try:
        cookie_list = json.loads(request.cookies.get('token_cookie', "[]"))
    except BaseException:
        cookie_list = []

    user_list, cookie_list = _get_user_list(cookie_list)

    if form.validate_on_submit():
        email = (form.email.data).lower()
        password = form.password.data
        remember_me = form.remember_me.data
        fast_log = form.fast_log.data

        user = User.get_by_email(email)
        if not user:
            form.email.errors.append("El email ingresado es incorrecto.")

        elif not user.check_password(password):
            form.password.errors.append("La contraseña ingresada es incorrecta.")

        else:
            login_user(user, remember=remember_me)

            next_page = request.form.get('next')
            if not next_page or url_parse(next_page).netloc == '':
                next_page = request.args.get('next')

            if not next_page:
                page = url_for('public.home')
            else:
                page = next_page

            # Fast-Log
            print("FastLog:",  int(bool(fast_log)))
            if user.token not in cookie_list:
                if int(bool(fast_log)):
                    if user.get_config_force("can_log_fast", 1).as_int():
                        cookie_list.append(user.token)
                    else:
                        flash("Las configuraciones de tu cuenta no permiten mantener tu cuenta en la lista de usuarios recientes.", "error")

            elif user.token in cookie_list:
                if (not int(bool(fast_log))) or (not user.get_config_force("can_log_fast", 1).as_int()):
                    cookie_list.remove(user.token)

            resp = make_response(redirect(page), 302)
            resp.set_cookie('token_cookie', json.dumps(cookie_list), max_age=datetime.timedelta(days=365))
            return resp

    else:
        user = User.get_by_token(user_token)
        if user is not None:
            can_log_fast = user.get_config_force("can_log_fast", 1).as_int()
            if can_log_fast:
                user_data = user
                form.email.data = user_data.email

    return render_template("auth/login.html", form=form, user_list=user_list, user_data=user_data)



@auth_bp.route("/auth/signup/", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        flash("Ya tienes una sesión iniciada.", "error")
        return redirect(url_for("public.home"))

    form = SignupForm()
    try:
        cookie_list = json.loads(request.cookies.get('token_cookie', "[]"))
    except BaseException:
        cookie_list = []

    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = str(form.lastname.data)
        email = (form.email.data).lower()
        password = form.password.data
        password_confirm = form.confirm.data
        remember_me = form.remember_me.data
        fast_log = form.fast_log.data

        if (password != password_confirm):
            form.password.errors.append("Las contraseñas no coinciden.")

        elif not User.get_by_email(email):
            user = User(email=email, username=f"{firstname} {lastname}".strip())
            user.set_password(password)
            user.save()

            profile = Profile(id_user=user.id, name=f"{firstname}", active=True)
            profile.save()

            user.set_config("can_log_fast", 1)
            login_user(user, remember=remember_me)
            flash("Usuario creado exitosamente.", "success")

            next_page = request.form.get('next')
            if not next_page or url_parse(next_page).netloc == '':
                next_page = request.args.get('next')

            if not next_page:
                page = url_for('profile.view_list')
            else:
                page = next_page

            # Cookie_List Token
            if user.token is not cookie_list:
                if int(bool(fast_log)):
                    cookie_list.append(user.token)

            resp = make_response(redirect(page), 302)
            resp.set_cookie('token_cookie', json.dumps(cookie_list), max_age=datetime.timedelta(days=365))
            return resp

        else:
            flash("El email ya está registrado, intente iniciar sesión.", "error")
            return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", form=form)


@auth_bp.route("/auth/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("public.home"))


@login_manager.user_loader
def load_user(user_id):
    logger.info(f"Usuario cargado: {user_id}")
    return User.get_by_id(user_id)
