"""Profile routes"""
import logging
import math
import random
from flask import render_template, request, redirect, abort, url_for
from flask_login import current_user, login_required


from . import profile_bp
from .forms import AddProfileForm

from app.models import Profile
from app.functions import calculate

logger = logging.getLogger(__name__)


@profile_bp.route("/update/", methods=["GET", "POST"])
@profile_bp.route("/update/<token>", methods=["GET", "POST"])
@login_required
def add(token=None):
    form = AddProfileForm()

    mode = "add"
    profile = None
    show_finish = True

    if form.validate_on_submit():
        name = form.profile.data
        active = int(form.status.data)

        # Crear el producto si no existe ninguno con el nombre ingresado:
        profile = None
        if token:
            profile = Profile.get_by_token(token)
            if not profile.id_user == current_user.id:
                profile = None
        
        if not profile:
            profile = Profile.get_by_name(name, current_user.id)

        if profile:
            profile.name = name
            profile.active = active
            profile.save()

        else:
            profile = Profile(
                id_user=current_user.id,
                name=name,
                active=active
            )
            profile.save()

        next_page = request.form.get('next', None)
        if not next_page or url_parse(next_page).netloc == "":
            next_page = url_for('profile.add')
            if token is not None:
                next_page = url_for('profile.details', token=token)
            
            elif form.submit_and_finish.data:
                next_page = url_for('profile.view_list')

        return redirect(next_page)

    else:
        if token is not None:
            profile = Profile.get_by_token(token)
            if profile is None or not profile.id_user == current_user.id:
                abort(404)
                
            form.profile.data = profile.name
            form.status.data = str(int(profile.active))
            mode = "edit"
            show_finish = False
        
    return render_template("profile/add.html", form=form, mode=mode, profile=profile, show_finish=show_finish)


@profile_bp.route("/list/", methods=["GET"])
@login_required
def view_list():
    profiles = Profile.get_by_user(current_user.id)    

    return render_template("profile/list.html", profiles=profiles)


@profile_bp.route("/details/<token>/", methods=["GET"])
@login_required
def details(token=None):
    profile = Profile.get_by_token(token)
    
    if profile is None:
        abort(404)

    if not profile.id_user == current_user.id:
        abort(404)   
    
    return render_template("profile/details.html", profile=profile, token=token)


@profile_bp.route("/discard/<token>/", methods=["GET"])
@login_required
def discard(token=None):
    profile = Profile.get_by_token(token)
    if profile is None or not profile.id_user == current_user.id:
        abort(404) 

    if profile.can_be_deleted():
        profile.delete()
        
    return redirect(url_for("profile.view_list"))


@profile_bp.route("/test/add/<int:number>/")
@login_required
def test_add(number):
    for i in range(int(number)):
        profile = Profile(
            id_user=current_user.id,
            name=f"Perfil Auto Generado {i}",
            active=True,
        )
        profile.save()

    return redirect(url_for("profile.view_list"))