"""Spending routes"""
import logging
import math
import random
import datetime
from flask import render_template, request, redirect, abort, url_for, flash
from flask_login import current_user, login_required


from . import spending_bp
from .forms import AddWorkDaySpendingForm

from app.models import WorkDay, ListSales, Spending, Profile
from app.functions import calculate
from app.decorators import profile_active_required

logger = logging.getLogger(__name__)


@spending_bp.route("/<workday_token>/update/", methods=["GET", "POST"])
@spending_bp.route("/<workday_token>/update/<token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def add(token=None, workday_token=None):
    form = AddWorkDaySpendingForm()
    form.profile.choices = [('none', 'General')]

    if token is None:
        form.profile.choices.append(('divide', 'Dividir entre todos'))

    number = 0
    profiles_to_divide = []
    for p in Profile.get_by_user(current_user.id, only_active=True):
        form.profile.choices.append((p.token, p.name.upper()))
        number += 1
        profiles_to_divide.append(p)

    show_finish = True
    mode = "add"
    spending = None
    error = 0
    workday = WorkDay.get_by_token(workday_token)
    if workday is None or not workday.id_user == current_user.id:
        abort(404)
    
    divide = False

    if form.validate_on_submit():
        profile_id = None

        spending_name = str(form.spending.data).upper()
        description = form.description.data
        try:
            price = calculate(form.price.data)
            if price < 1:
                form.price.errors.append("Monto mínimo: $1")
                error = 0

        except BaseException:
            form.price.errors.append("Verifique el número ingresado.")
            error += 1
        
        profile_token = form.profile.data
        hidden_token = form.hidden_token.data

        # Crear el producto si no existe ninguno con el nombre ingresado:
        if token:
            spending = Spending.get_by_token(token)
            if not spending.id_workday == workday.id:
                spending = None

        if len(description) == 0:
            description = None

        if profile_token not in ("none", "divide"):
            profile = Profile.get_by_token(profile_token)
            if profile is not None and profile.id_user == current_user.id:
                profile_id = profile.id

        elif profile_token == "divide":
            divide = True

        else:
            profile_token = None
        
        if error == 0:
            if divide:
                price, extra_price = divmod(price, number)

                n = 1
                for profile in profiles_to_divide:
                    spending = Spending(
                        id_workday=workday.id,
                        id_profile=profile.id,
                        name=f"{spending_name} ({n}/{number})",
                        description=description,
                        price=price + int(n <= extra_price),
                    )
                    spending.save()
                    n += 1

            elif spending:
                spending.name = spending_name
                spending.description = description
                spending.price = price
                spending.id_profile = profile_id
                spending.save()

            else:
                spending = Spending(
                    id_workday=workday.id,
                    id_profile=profile_id,
                    name=spending_name,
                    description=description,
                    price=price,
                )
                spending.save()

            next_page = request.form.get('next', None)
            if not next_page or url_parse(next_page).netloc == "":
                next_page = url_for('spending.add', workday_token=workday.token)
                if token is not None:
                    next_page = url_for('spending.details', token=token)
                
                elif form.submit_and_finish.data:
                    next_page = url_for('spending.view_list', workday_token=workday.token)

            return redirect(next_page)

    else:
        if token is not None:
            spending = Spending.get_by_token(token)
            if spending is None or not spending.id_workday == workday.id:
                abort(404)
                
            form.spending.data = str(spending.name).upper()
            form.price.data = str(spending.price)

            form.profile.data = spending.get_profile_token()
            mode = "edit"
            show_finish = False
        
    return render_template(
        "spending/add.html", error=error, show_finish=show_finish,\
            form=form, mode=mode, workday=workday, spending=spending
    )


@spending_bp.route("/list/<workday_token>/", methods=["GET"])
@login_required
@profile_active_required
def view_list(workday_token=None):
    workday = WorkDay.get_by_token(workday_token)
    if workday is None or not workday.id_user == current_user.id:
        abort(404) 
  
    spendings = workday.get_spendings()

    return render_template("spending/list.html", spendings=spendings, workday=workday)


@spending_bp.route("/details/<token>/", methods=["GET"])
@login_required
@profile_active_required
def details(token=None,):
    spending = Spending.get_by_token(token)
    if spending is None:
        abort(404) 

    workday = spending.workday
    if workday is None or not workday.id_user == current_user.id:
        abort(404) 
        
    return render_template("spending/details.html", workday=workday, token=token, spending=spending)


@spending_bp.route("/discard/<token>/", methods=["GET"])
@login_required
@profile_active_required
def discard(token=None):
    spending = Spending.get_by_token(token)
    if spending is None:
        abort(404) 

    workday = spending.workday
    if workday is None or not workday.id_user == current_user.id:
        abort(404) 

    spending.delete()
        
    return redirect(url_for("spending.view_list", workday_token=workday.token))

