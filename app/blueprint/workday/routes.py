"""Workday routes"""
import logging
import math
import random
import datetime
from flask import render_template, request, redirect, abort, url_for, flash
from flask_login import current_user, login_required


from . import workday_bp
from .forms import AddWorkDayForm, AddWorkDayProductForm, SearchWorkdayForm, NoteWorkDayForm

from app.models import Product, WorkDay, ListSales, Spending, Profile, GroupSale
from app.functions import calculate, analyze_int_fields, analyze_str_fields
from app.decorators import profile_active_required

logger = logging.getLogger(__name__)


@workday_bp.route("/update/", methods=["GET", "POST"])
@workday_bp.route("/update/<token>", methods=["GET", "POST"])
@login_required
@profile_active_required
def add(token=None):
    form = AddWorkDayForm()

    mode = "add"
    error = 0
    workday = None

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

        # Crear el producto si no existe ninguno con el nombre ingresado:
        if error == 0:
            workday = None
            if token:
                workday = WorkDay.get_by_token(token)
                if not workday.id_user == current_user.id:
                    workday = None

            if workday is None:
                workday = WorkDay.get_by_date(current_user.id, date)
            
            if workday:
                workday.date = date
                workday.note = note
                workday.save()
                token = workday.token

            else:
                group_sale = GroupSale()
                group_sale.save()

                workday = WorkDay(
                    id_user=current_user.id,
                    id_group_sale=group_sale.id,
                    date=date,
                    note=note
                )
                workday.save()

                token = workday.token

            next_page = request.form.get('next', None)
            if not next_page or url_parse(next_page).netloc == "":
                next_page = url_for('workday.view_list')
                if token is not None:
                    next_page = url_for('workday.details', token=token)

            return redirect(next_page)

    else:
        form.date.data = datetime.datetime.utcnow().strftime("%d/%m/%Y")
        if token is not None:
            workday = WorkDay.get_by_token(token)
            if workday is None or not workday.id_user == current_user.id:
                abort(404)
                
            form.date.data = workday.date.strftime("%d/%m/%Y")
            form.note.data = workday.note
            mode = "edit"
        
    return render_template(
        "workday/add.html", form=form, mode=mode, workday=workday, error=error
    )


@workday_bp.route("/list/", methods=["GET"])
@login_required
@profile_active_required
def view_list():
    form = SearchWorkdayForm()
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

        min_sales = int(request.args.get("min_sales", "0"))
        max_sales = int(request.args.get("max_sales", "1"+"0"*50))

        workdays = []

        advanced = False
        for _name in ("min_price", "max_price", "min_cost", "max_cost", "min_profit", "max_profit", "min_sales", "max_sales"):
            if not request.args.get(_name, None) is None:
                advanced = True
                break

        total = 0
        for workday in WorkDay.get_by_user(current_user.id):
            total += 1
            sales = workday.get_mount_of_sales()
            quantity = sales.get("quantity", 0)
            price = sales.get("price", 0)
            cost = sales.get("cost", 0)
            profit = sales.get("profit", 0)

            if price >= min_price and price <= max_price and\
                cost >= min_cost and cost <= max_cost and\
                    profit >= min_profit and profit <= max_profit and\
                        quantity >= min_sales and quantity <= max_sales:

                if workday.between(min_date, max_date, format_date):
                    workdays.append(workday)

        
        search_data['advanced'] = advanced
        search_data['results'] = len(workdays)
        search_data['total'] = total

    else:
        workdays = WorkDay.get_by_user(current_user.id)

    return render_template("workday/list.html", workdays=workdays, search=search, search_data=search_data, form=form)


@workday_bp.route("/list/search/", methods=["POST"])
@login_required
@profile_active_required
def list_search():
    form = SearchWorkdayForm()
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
        # Sales
        min_sales, error = analyze_int_fields(form.min_sales, None)
        max_sales, error = analyze_int_fields(form.max_sales, None)

    if error == 0:
        return redirect(
            url_for(
                "workday.view_list", search='true', min_price=min_price, max_price=max_price, min_date=min_date, max_date=max_date,
                min_cost=min_cost, max_cost=max_cost, min_profit=min_profit, max_profit=max_profit, min_sales=min_sales, max_sales=max_sales,
            )
        )

    else:
        return view_list()


@workday_bp.route("/details/<token>/", methods=["GET"])
@login_required
@profile_active_required
def details(token=None):
    form = NoteWorkDayForm()
    workday = WorkDay.get_by_token(token)
    if workday is None:
        abort(404)

    if not workday.id_user == current_user.id:
        abort(404) 
        
    resume = request.args.get("resume", None) in ("true", "True")
    by_unit = request.args.get("by_unit", "true") in ("true", "True")
        
    sales = workday.get_sales()
    if resume:
        total = workday.get_resume(sales)
    else:
        total = None

    form.note.data = workday.note
    
    simple = int(request.args.get("simple", current_user.get_simple_mode()))
    if simple:
        html_file = "workday/simple/details.html"
    else:
        html_file = "workday/details.html"

    return render_template(html_file, workday=workday, token=token, sales=sales, total=total, by_unit=by_unit, form=form)



@workday_bp.route("/discard/<token>/", methods=["GET"])
@login_required
@profile_active_required
def discard(token=None):
    workday = WorkDay.get_by_token(token)
    if workday is None or not workday.id_user == current_user.id:
        abort(404) 

    if workday.can_be_deleted():
        group_sale = workday.group_sale
        group_sale.delete_all_sales()
        workday.delete()
        group_sale.delete()
        
    return redirect(url_for("workday.view_list"))



@workday_bp.route("/note/set/<token>/", methods=["POST"])
@login_required
@profile_active_required
def set_note(token):
    form = NoteWorkDayForm()
    error = 0

    workday = WorkDay.get_by_token(token)
    if workday is None:
        abort(404)

    if not workday.id_user == current_user.id:
        abort(404) 

    if form.validate_on_submit():
        # note
        note, error = analyze_str_fields(form.note, None)

        if note is not None:
            if len(note) == 0:
                note = None

        if error == 0:
            workday.note = note
            workday.save()

    return redirect(url_for("workday.details", token=token, **request.args))



@workday_bp.route("/stats/", methods=["GET"])
@login_required
@profile_active_required
def stats():
    graphics = request.args.get("graphics") in ("true", "True")
    profiles = Profile.get_by_user(current_user.id, only_active=True)
        
    workdays = WorkDay.get_by_user(current_user.id)

    total = {
        'quantity': 0,
        'price': 0,
        'cost': 0,
        'profit': 0,
        'profit_profile': 0,
        'default_price': 0,
        'percent_price_cost': 0,
        'percent_profit_cost': 0,
        'workdays_count': 0,
        'profiles': {profile: {'spending': 0, 'spending_count': 0, 'max_profit': 0} for profile in profiles},
        'max_price': 0,
        'max_profit': 0,
        'spendings_total': 0,
        'spendings_total_count': 0,
        'spendings_general': 0,
        'spendings_general_count': 0,
    }
    months = {}
    data_workdays = {}

    for workday in workdays:
        sales = workday.get_sales()
        spendings_list = workday.get_spendings()
        resume = workday.get_resume(sales, spendings_list, profiles=profiles)
        data_workdays[workday] = {'sales': sales, 'resume': resume}

        spendings = resume['spendings']

        total['quantity'] += resume['quantity']
        total['price'] += resume['price']
        total['cost'] += resume['cost']
        total['profit'] += resume['profit']
        total['profit_profile'] += resume['profit_profile']
        total['default_price'] += resume['default_price']
        total['workdays_count'] += 1
        total['spendings_total'] += spendings['total']
        total['spendings_general'] += spendings['general_spending']
        total['spendings_total_count'] += spendings['count']
        total['spendings_general_count'] += spendings['general_count']
        


        total['max_price'] = max(total['max_price'], resume['price'])
        total['max_profit'] = max(total['max_profit'], resume['profit'])
         
        month = workday.get_date_as_tuple()[0:2]

        if not month in months:
            months[month] = {
                'quantity': 0,
                'price': 0,
                'cost': 0,
                'profit': 0,
                'default_price': 0,
                'workdays_count': 0,
                'profit_profile': 0,
                'max_price': 0,
                'max_profit': 0,
                'profiles': {profile: {'spending': 0, 'spending_count': 0, 'max_profit': 0,} for profile in profiles},
                'workdays': [],
                'spendings_total': 0,
                'spendings_total_count': 0,
                'spendings_general': 0,
                'spendings_general_count': 0,
            }

        dmonth = months[month]

        dmonth['quantity'] += resume['quantity']
        dmonth['price'] += resume['price']
        dmonth['cost'] += resume['cost']
        dmonth['profit'] += resume['profit']
        dmonth['profit_profile'] += resume['profit_profile']
        dmonth['default_price'] += resume['default_price']
        dmonth['workdays_count'] += 1
        dmonth['workdays'].append(workday)

        dmonth['spendings_total'] += spendings['total']
        dmonth['spendings_general'] += spendings['general_spending']
        dmonth['spendings_total_count'] += spendings['count']
        dmonth['spendings_general_count'] += spendings['general_count']

        dmonth['max_price'] = max(dmonth['max_price'], resume['price'])
        dmonth['max_profit'] = max(dmonth['max_profit'], resume['profit'])


        for profile, p_resume in resume['spendings']['profiles'].items():
            if profile in total['profiles']:
                dc = total['profiles'][profile]
                dc['spending'] += p_resume['spending']
                dc['spending_count'] += p_resume['count']
                dc['max_profit'] = max(dc['max_profit'], resume['profit_profile']-p_resume['spending'])

            if profile in dmonth['profiles']:
                dc = dmonth['profiles'][profile]
                dc['spending'] += p_resume['spending']
                dc['spending_count'] += p_resume['count']
                dc['max_profit'] = max(dc['max_profit'], resume['profit_profile']-p_resume['spending'])

        
        try:
            dmonth['percent_profit_cost'] = round(100*dmonth['profit'] / dmonth['cost'], 2)
        except ZeroDivisionError:
            dmonth['percent_profit_cost'] = 0

        try:
            dmonth['percent_profit_price'] = round(100*dmonth['profit'] / dmonth['price'], 2)
        except ZeroDivisionError:
            dmonth['percent_profit_price'] = 0

    
    # Total
    try:
        total['percent_profit_cost'] = round(100*total['profit'] / total['cost'], 2)
    except ZeroDivisionError:
        total['percent_profit_cost'] = 0

    try:
        total['percent_profit_price'] = round(100*total['profit'] /  total['price'], 2)
    except ZeroDivisionError:
        total['percent_profit_price'] = 0

 
    return render_template(
        "workday/stat.html", workdays=workdays, total=total,\
            months=months, data_workdays=data_workdays, graphics=graphics
        )



@workday_bp.route("/p/update/<token>/", methods=["GET", "POST"])
@workday_bp.route("/p/update/<token>/pr/<product_token>/", methods=["GET", "POST"])
@workday_bp.route("/p/update/<token>/ls/<list_sale_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def product_add(token=None, product_token=None, list_sale_token=None):
    form = AddWorkDayProductForm()
    
    workday = WorkDay.get_by_token(token)
    if workday is None:
        abort(404)

    if not workday.id_user == current_user.id:
        abort(404) 

    mode = "add"
    show_finish = True
    sale = None
    product = None
    error = 0

    if list_sale_token is not None:
        sale = ListSales.get_by_token(list_sale_token)
        if sale is None or not sale.id_group_sale == workday.id_group_sale:
            abort(404)

        product_token = None
        product = sale.cost.product
        mode = "edit"
        show_finish = False

    if product_token is not None:
        product = Product.get_by_token(product_token)
        if product is None or not product.id_user == current_user.id:
            abort(404)
            
    if form.validate_on_submit():
        hidden_token = form.hidden_token.data
        try:
            price = calculate(form.price.data)

        except BaseException:
            form.quantity.errors.append("Verifique el número ingresado.")
            error += 1

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
            if sale is None and quantity > product.get_stock():
                form.quantity.errors.append("El stock del producto es insuficiente.")
                error += 1

            elif sale is not None and quantity > product.get_stock() + sale.quantity :
                form.quantity.errors.append("El stock del producto es insuficiente.")
                error += 1

            if error == 0:
                cost = product.get_current_cost()

                if list_sale_token is None:
                    sale = ListSales.get_by_price_cost_and_group_sale(id_group_sale=workday.id_group_sale, id_cost=cost.id, price=int(price))
                    if sale is not None:
                        sale.quantity += quantity
                    else:
                        sale = ListSales(id_group_sale=workday.id_group_sale, id_cost=cost.id, price=int(price), quantity=int(quantity))
                
                else:
                    sale.quantity = quantity
                    sale.price = price

                sale.save()

                next_page = request.form.get('next', None)
                if not next_page or url_parse(next_page).netloc == "":
                    next_page = url_for('workday.view_list')

                    if form.submit.data:
                        next_page = url_for('workday.product_add', token=token)

                    elif token is not None:
                        next_page = url_for('workday.details', token=token)

                return redirect(next_page)

    if product is not None:
        product_token = product.token
        p_cost = product.get_cost(workday.date)
        form.product.data = product.name
        form.cost.data = str(p_cost.cost)
        form.extra_cost.data = str(p_cost.extra_cost)
        form.quantity.data = "1"
        form.price.data = str(p_cost.get_price())

        if list_sale_token is not None:
            if sale:
                form.price.data = str(sale.price)
                form.quantity.data = str(sale.quantity)
        
    return render_template(
        "workday/add_product.html", form=form, mode=mode, show_finish=show_finish,\
            workday=workday, product=product, sale=sale, error=error
    )




@workday_bp.route("/discard/<token>/ls/<list_sale_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def product_delete_sale(token=None, list_sale_token=None):
    form = None
    
    workday = WorkDay.get_by_token(token)
    if workday is None:
        abort(404)

    if not workday.id_user == current_user.id:
        abort(404) 

    sale = None
    if list_sale_token is not None:
        sale = ListSales.get_by_token(list_sale_token)
        if sale is None or not sale.id_group_sale == workday.id_group_sale:
            abort(404)

        sale.delete()

    return redirect(url_for("workday.details", token=token))


@workday_bp.route("/details/<token>/ls/<list_sale_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def product_sale_details(token=None, list_sale_token=None):
    form = None
    
    workday = WorkDay.get_by_token(token)
    if workday is None or not workday.id_user == current_user.id:
        abort(404) 

    sale = None
    product = None
    cost = None
    if list_sale_token is not None:
        sale = ListSales.get_by_token(list_sale_token)
        if sale is None or not sale.id_group_sale == workday.id_group_sale:
            abort(404)

        cost = sale.cost
        product = cost.product


    
    profiles = Profile.get_by_user(current_user.id, only_active=True)

    return render_template(
        "workday/sale_details.html", workday=workday, product=product, cost=cost, sale=sale, profiles=profiles
    )
