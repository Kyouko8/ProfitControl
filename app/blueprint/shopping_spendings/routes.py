"""Spending routes"""
import datetime
import logging
import math
import random

from app.models.models import (ListShopping, Profile, ShoppingDay,
                               ShoppingSpending)
from app.utils.decorators import profile_active_required
from app.utils.functions import calculate
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import s_spending_bp
from .forms import AddShoppingDaySpendingForm

logger = logging.getLogger(__name__)


@s_spending_bp.route("/<shoppingday_token>/update/", methods=["GET", "POST"])
@s_spending_bp.route("/<shoppingday_token>/update/<token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def add(token=None, shoppingday_token=None):
    form = AddShoppingDaySpendingForm()

    show_finish = True
    mode = "add"
    spending = None
    error = 0
    shoppingday = ShoppingDay.get_by_token(shoppingday_token)
    if shoppingday is None or not shoppingday.id_user == current_user.id:
        abort(404)

    if form.validate_on_submit():

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

        # Crear el producto si no existe ninguno con el nombre ingresado:
        if token:
            spending = ShoppingSpending.get_by_token(token)
            if not spending.id_shoppingday == shoppingday.id:
                spending = None

        if len(description) == 0:
            description = None
        
        if error == 0:
            if spending:
                spending.name = spending_name
                spending.description = description
                spending.price = price
                spending.save()

            else:
                spending = ShoppingSpending(
                    id_shoppingday=shoppingday.id,
                    name=spending_name,
                    description=description,
                    price=price,
                )
                spending.save()

            next_page = request.form.get('next', None)
            if not next_page or url_parse(next_page).netloc == "":
                next_page = url_for('shopping_spending.add', shoppingday_token=shoppingday.token)
                if token is not None:
                    next_page = url_for('shopping_spending.details', token=token)
                
                elif form.submit_and_finish.data:
                    next_page = url_for('shopping_spending.view_list', shoppingday_token=shoppingday.token)

            return redirect(next_page)

    else:
        if token is not None:
            spending = ShoppingSpending.get_by_token(token)
            if spending is None or not spending.id_shoppingday == shoppingday.id:
                abort(404)
                
            form.spending.data = str(spending.name).upper()
            form.price.data = str(spending.price)

            mode = "edit"
            show_finish = False
        
    return render_template(
        "shopping_spending/add.html", error=error, show_finish=show_finish,\
            form=form, mode=mode, shoppingday=shoppingday, spending=spending
    )


@s_spending_bp.route("/list/<shoppingday_token>/", methods=["GET"])
@login_required
@profile_active_required
def view_list(shoppingday_token=None):
    shoppingday = ShoppingDay.get_by_token(shoppingday_token)
    if shoppingday is None or not shoppingday.id_user == current_user.id:
        abort(404) 
  
    spendings = shoppingday.get_spendings()

    return render_template("shopping_spending/list.html", spendings=spendings, shoppingday=shoppingday)


@s_spending_bp.route("/details/<token>/", methods=["GET"])
@login_required
@profile_active_required
def details(token=None,):
    spending = ShoppingSpending.get_by_token(token)
    if spending is None:
        abort(404) 

    shoppingday = spending.shoppingday
    if shoppingday is None or not shoppingday.id_user == current_user.id:
        abort(404) 
        
    return render_template("shopping_spending/details.html", shoppingday=shoppingday, token=token, spending=spending)


@s_spending_bp.route("/discard/<token>/", methods=["GET"])
@login_required
@profile_active_required
def discard(token=None):
    spending = ShoppingSpending.get_by_token(token)
    if spending is None:
        abort(404) 

    shoppingday = spending.shoppingday
    if shoppingday is None or not shoppingday.id_user == current_user.id:
        abort(404) 

    spending.delete()
        
    return redirect(url_for("shopping_spending.view_list", shoppingday_token=shoppingday.token))

