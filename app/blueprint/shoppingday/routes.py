"""ShoppingDay routes"""
import logging
import math
import random
import datetime
from flask import render_template, request, redirect, abort, url_for, flash
from flask_login import current_user, login_required


from . import shoppingday_bp
from .forms import AddShoppingDayForm, AddShoppingDayProductForm, SearchShoppingDayForm, NoteShoppingDayForm

from app.models import Product, ShoppingDay, ListShopping, Profile, GroupShopping
from app.functions import calculate, analyze_int_fields, analyze_str_fields
from app.decorators import profile_active_required

logger = logging.getLogger(__name__)


@shoppingday_bp.route("/update/", methods=["GET", "POST"])
@shoppingday_bp.route("/update/<token>", methods=["GET", "POST"])
@login_required
@profile_active_required
def add(token=None):
    form = AddShoppingDayForm()

    mode = "add"
    error = 0
    shoppingday = None

    if form.validate_on_submit():
        date = None
        for date_format in ["%d-%m-%Y", "%d-%m-%y", "%d/%m/%Y", "%d/%m/%y", ]:
            try:
                date = datetime.datetime.strptime(form.date.data.replace(" ", ""), date_format)
                break
            except ValueError:
                pass

        if date is None:
            error += 1
            form.date.errors.append("El formato de fecha ingresado es inválido.")

        note = form.note.data

        if len(note) == 0:
            note = None

        if error == 0:
            shoppingday = None
            if token:
                shoppingday = ShoppingDay.get_by_token(token)
                if not shoppingday.id_user == current_user.id:
                    shoppingday = None

            if shoppingday is None:
                shoppingday = ShoppingDay.get_by_date(current_user.id, date)
            
            if shoppingday:
                shoppingday.date = date
                shoppingday.note = note
                shoppingday.save()
                token = shoppingday.token

            else:
                group_shopping = GroupShopping()
                group_shopping.save()

                shoppingday = ShoppingDay(
                    id_user=current_user.id,
                    id_group_shopping=group_shopping.id,
                    date=date,
                    note=note
                )
                shoppingday.save()

                token = shoppingday.token

            next_page = request.form.get('next', None)
            if not next_page or url_parse(next_page).netloc == "":
                next_page = url_for('shoppingday.view_list')
                if token is not None:
                    next_page = url_for('shoppingday.details', token=token)

            return redirect(next_page)

    else:
        form.date.data = datetime.datetime.utcnow().strftime("%d/%m/%Y")
        if token is not None:
            shoppingday = ShoppingDay.get_by_token(token)
            if shoppingday is None or not shoppingday.id_user == current_user.id:
                abort(404)
                
            form.date.data = shoppingday.date.strftime("%d/%m/%Y")
            mode = "edit"
        
    return render_template(
        "shoppingday/add.html", form=form, mode=mode, shoppingday=shoppingday, error=error
    )


@shoppingday_bp.route("/list/", methods=["GET"])
@login_required
@profile_active_required
def view_list():
    form = SearchShoppingDayForm()
    search = (request.args.get("search", "False") in ("true", "True"))
    search_data = {}
    if search:
        min_date = request.args.get("min_date", None)
        max_date = request.args.get("max_date", None)
        format_date = request.args.get("format_date", "%d/%m/%Y")

        min_price = int(request.args.get("min_price", "0"))
        max_price = int(request.args.get("max_price", "1"+"0"*50))

        min_cost = int(request.args.get("min_cost", "0"))
        max_cost = int(request.args.get("max_cost", "1"+"0"*50))

        min_profit = int(request.args.get("min_profit", "0"))
        max_profit = int(request.args.get("max_profit", "1"+"0"*50))

        min_shoppings = int(request.args.get("min_shoppings", "0"))
        max_shoppings = int(request.args.get("max_shoppings", "1"+"0"*50))

        shoppingdays = []

        advanced = False
        for _name in ("min_price", "max_price", "min_cost", "max_cost", "min_profit", "max_profit", "min_shoppings", "max_shoppings"):
            if not request.args.get(_name, None) is None:
                advanced = True
                break

        total = 0
        for shoppingday in ShoppingDay.get_by_user(current_user.id):
            total += 1
            shoppings = shoppingday.get_mount_of_shoppings()
            quantity = shoppings.get("quantity", 0)
            price = shoppings.get("price", 0)
            cost = shoppings.get("cost", 0)
            profit = shoppings.get("profit", 0)

            if price >= min_price and price <= max_price and\
                cost >= min_cost and cost <= max_cost and\
                    profit >= min_profit and profit <= max_profit and\
                        quantity >= min_shoppings and quantity <= max_shoppings:

                if shoppingday.between(min_date, max_date, format_date):
                    shoppingdays.append(shoppingday)

        
        search_data['advanced'] = advanced
        search_data['results'] = len(shoppingdays)
        search_data['total'] = total

    else:
        shoppingdays = ShoppingDay.get_by_user(current_user.id)

    return render_template("shoppingday/list.html", shoppingdays=shoppingdays, search=search, search_data=search_data, form=form)


@shoppingday_bp.route("/list/search/", methods=["POST"])
@login_required
@profile_active_required
def list_search():
    form = SearchShoppingDayForm()
    error = 0

    if form.validate_on_submit():
        # Price
        min_price, error = analyze_int_fields(form.min_price, None)
        max_price, error = analyze_int_fields(form.max_price, None)
        # Date
        min_date, error = analyze_str_fields(form.min_date, None)
        max_date, error = analyze_str_fields(form.max_date, None)
        # Cost
        min_cost, error = analyze_int_fields(form.min_cost, None)
        max_cost, error = analyze_int_fields(form.max_cost, None)
        # Profit
        min_profit, error = analyze_int_fields(form.min_profit, None)
        max_profit, error = analyze_int_fields(form.max_profit, None)
        # shoppings
        min_shoppings, error = analyze_int_fields(form.min_shoppings, None)
        max_shoppings, error = analyze_int_fields(form.max_shoppings, None)

    if error == 0:
        return redirect(
            url_for(
                "shoppingday.view_list", search='true', min_price=min_price, max_price=max_price, min_date=min_date, max_date=max_date,
                min_shoppings=min_shoppings, max_shoppings=max_shoppings,
                # min_cost=min_cost, max_cost=max_cost, min_profit=min_profit, max_profit=max_profit,
            )
        )

    else:
        return view_list()


@shoppingday_bp.route("/details/<token>/", methods=["GET"])
@login_required
@profile_active_required
def details(token=None):
    form = NoteShoppingDayForm()
    shoppingday = ShoppingDay.get_by_token(token)
    if shoppingday is None:
        abort(404)

    if not shoppingday.id_user == current_user.id:
        abort(404) 
        
    resume = request.args.get("resume", None) in ("true", "True")
    by_unit = request.args.get("by_unit", "true") in ("true", "True")
        
    shoppings = shoppingday.get_shoppings()
    if resume:
        total = shoppingday.get_resume(shoppings)
    else:
        total = None

    form.note.data = shoppingday.note
    
    simple = int(request.args.get("simple", current_user.get_simple_mode()))
    if simple:
        html_file = "shoppingday/simple/details.html"
    else:
        html_file = "shoppingday/details.html"

    return render_template(html_file, shoppingday=shoppingday, token=token, shoppings=shoppings, total=total, by_unit=by_unit, form=form)



@shoppingday_bp.route("/discard/<token>/", methods=["GET"])
@login_required
@profile_active_required
def discard(token=None):
    shoppingday = ShoppingDay.get_by_token(token)
    if shoppingday is None or not shoppingday.id_user == current_user.id:
        abort(404) 

    if shoppingday.can_be_deleted():
        group_shopping = shoppingday.group_shopping
        group_shopping.delete_all_shoppings()
        shoppingday.delete()
        group_shopping.delete()
        
    return redirect(url_for("shoppingday.view_list"))


@shoppingday_bp.route("/note/set/<token>/", methods=["POST"])
@login_required
@profile_active_required
def set_note(token):
    form = NoteShoppingDayForm()
    error = 0

    shoppingday = ShoppingDay.get_by_token(token)
    if shoppingday is None or not shoppingday.id_user == current_user.id:
        abort(404) 

    if form.validate_on_submit():
        # note
        note, error = analyze_str_fields(form.note, None)

        if note is not None:
            if len(note) == 0:
                note = None

        if error == 0:
            shoppingday.note = note
            shoppingday.save()

    return redirect(url_for("shoppingday.details", token=token, **request.args))


@shoppingday_bp.route("/p/update/<token>/", methods=["GET", "POST"])
@shoppingday_bp.route("/p/update/<token>/pr/<product_token>/", methods=["GET", "POST"])
@shoppingday_bp.route("/p/update/<token>/ls/<list_shopping_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def product_add(token=None, product_token=None, list_shopping_token=None):
    form = AddShoppingDayProductForm()
    
    shoppingday = ShoppingDay.get_by_token(token)
    if shoppingday is None:
        abort(404)

    if not shoppingday.id_user == current_user.id:
        abort(404) 

    mode = "add"
    show_finish = True
    shopping = None
    product = None
    error = 0

    if list_shopping_token is not None:
        shopping = ListShopping.get_by_token(list_shopping_token)
        if shopping is None or not shopping.id_group_shopping == shoppingday.id_group_shopping:
            abort(404)

        product_token = None
        product = shopping.cost.product
        mode = "edit"
        show_finish = False

    if product_token is not None:
        product = Product.get_by_token(product_token)
        if product is None or not product.id_user == current_user.id:
            abort(404)
            
    if form.validate_on_submit():
        try:
            quantity = calculate(form.quantity.data)
        except BaseException:
            form.quantity.errors.append("Verifique el número ingresado.")
            error += 1
        
        if product is None:
            product = Product.get_by_name(form.product.data, current_user.id)

            if product is None:
                form.product.errors.append("El nombre del producto ingresado no existe.")
                
        if product is not None:
            if error == 0:
                cost = product.get_current_cost()

                if list_shopping_token is None:
                    shopping = ListShopping.get_by_cost_and_group_shopping(id_group_shopping=shoppingday.id_group_shopping, id_cost=cost.id)
                    if shopping is not None:
                        shopping.quantity += quantity
                    else:
                        shopping = ListShopping(id_group_shopping=shoppingday.id_group_shopping, id_cost=cost.id, quantity=int(quantity))
                
                else:
                    shopping.quantity = quantity

                shopping.save()

                next_page = request.form.get('next', None)
                if not next_page or url_parse(next_page).netloc == "":
                    next_page = url_for('shoppingday.view_list')

                    if form.submit.data:
                        next_page = url_for('shoppingday.product_add', token=token)

                    elif token is not None:
                        next_page = url_for('shoppingday.details', token=token)

                return redirect(next_page)

    if product is not None:
        product_token = product.token
        p_cost = product.get_cost(shoppingday.date)
        form.product.data = product.name
        form.cost.data = str(p_cost.cost)
        form.extra_cost.data = str(p_cost.extra_cost)
        form.quantity.data = "1"
        form.price.data = str(p_cost.get_price())

        if list_shopping_token is not None:
            if shopping:
                form.quantity.data = str(shopping.quantity)
        
    return render_template(
        "shoppingday/add_product.html", form=form, mode=mode, show_finish=show_finish,\
            shoppingday=shoppingday, product=product, shopping=shopping, error=error
    )




@shoppingday_bp.route("/discard/<token>/ls/<list_shopping_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def product_delete_shopping(token=None, list_shopping_token=None):
    form = None
    
    shoppingday = ShoppingDay.get_by_token(token)
    if shoppingday is None:
        abort(404)

    if not shoppingday.id_user == current_user.id:
        abort(404) 

    shopping = None
    if list_shopping_token is not None:
        shopping = ListShopping.get_by_token(list_shopping_token)
        if shopping is None or not shopping.id_group_shopping == shoppingday.id_group_shopping:
            abort(404)

        shopping.delete()

    return redirect(url_for("shoppingday.details", token=token))


@shoppingday_bp.route("/details/<token>/ls/<list_shopping_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def product_shopping_details(token=None, list_shopping_token=None):
    form = None
    
    shoppingday = ShoppingDay.get_by_token(token)
    if shoppingday is None or not shoppingday.id_user == current_user.id:
        abort(404) 

    shopping = None
    product = None
    cost = None
    if list_shopping_token is not None:
        shopping = ListShopping.get_by_token(list_shopping_token)
        if shopping is None or not shopping.id_group_shopping == shoppingday.id_group_shopping:
            abort(404)

        cost = shopping.cost
        product = cost.product


    
    profiles = Profile.get_by_user(current_user.id, only_active=True)

    return render_template(
        "shoppingday/shopping_details.html", shoppingday=shoppingday, product=product, cost=cost, shopping=shopping, profiles=profiles
    )
