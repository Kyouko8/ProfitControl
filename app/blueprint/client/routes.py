"""Workday routes"""
import logging
import math
import random
import datetime
from flask import render_template, request, redirect, abort, url_for, flash
from flask_login import current_user, login_required


from . import client_bp
from .forms import AddClientForm, AddClientProductForm, SearchClientForm, NoteForm

from app.models import Product, Client, ClientSale, ListSales, Spending, Profile, GroupSale
from app.functions import calculate, analyze_int_fields, analyze_str_fields
from app.decorators import profile_active_required

logger = logging.getLogger(__name__)


@client_bp.route("/update/", methods=["GET", "POST"])
@client_bp.route("/update/<token>", methods=["GET", "POST"])
@login_required
@profile_active_required
def add(token=None):
    form = AddClientForm()
    show_all_fields = request.args.get("fields", "false") in ("True", "TRUE", "true")

    mode = "add"
    error = 0
    client = None

    if form.validate_on_submit():
        name, error = analyze_str_fields(form.name, default="Sin Nombre")
        description, error = analyze_str_fields(form.description)
        telephone, error = analyze_str_fields(form.telephone)
        telephone_alt, error = analyze_str_fields(form.telephone_alt)
        phone_number, error = analyze_str_fields(form.phone_number)
        phone_number_alt, error = analyze_str_fields(form.phone_number_alt)
        email, error = analyze_str_fields(form.email)
        address, error = analyze_str_fields(form.address)
        location, error = analyze_str_fields(form.location)

        note = form.note.data

        if len(note) == 0:
            note = None

        name = name.upper()
        # Crear el producto si no existe ninguno con el nombre ingresado:
        if error == 0:
            client = None
            if token:
                client = Client.get_by_token(token)
                if not client.id_user == current_user.id:
                    client = None

            if client is None:
                client = Client.get_by_name(current_user.id, name)
            
            if client:
                client.name = name.upper()
                client.description = description
                client.telephone = telephone
                client.telephone_alt = telephone_alt
                client.phone_number = phone_number
                client.phone_number_alt = phone_number_alt
                client.address = address
                client.email = email
                client.location = location
                client.note = note
                client.save()
                token = client.token

            else:
                group_sale = GroupSale()
                group_sale.save()

                client = Client(
                    id_user=current_user.id,
                    id_group_sale=group_sale.id,
                    name=name.upper(),
                    description=description,
                    telephone=telephone,
                    telephone_alt=telephone_alt,
                    phone_number=phone_number,
                    phone_number_alt=phone_number_alt,
                    address=address,
                    email=email,
                    location=location,
                    note=note
                )
                client.save()

                token = client.token

            next_page = request.form.get('next', None)
            if not next_page or url_parse(next_page).netloc == "":
                next_page = url_for('client.view_list')
                if token is not None:
                    next_page = url_for('client.details', token=token)

            return redirect(next_page)

    else:
        if token is not None:
            client = Client.get_by_token(token)
            if client is None or not client.id_user == current_user.id:
                abort(404)
                
            form.name.data = client.name
            form.description.data = client.description
            form.telephone.data = client.telephone
            form.telephone_alt.data = client.telephone_alt
            form.phone_number.data = client.phone_number
            form.phone_number_alt.data = client.phone_number_alt
            form.address.data = client.address
            form.email.data = client.email
            form.location.data = client.location
            form.note.data = client.note
            mode = "edit"
        
    return render_template(
        "client/add.html", form=form, mode=mode, client=client, error=error, show_all_fields=show_all_fields
    )


@client_bp.route("/list/", methods=["GET"])
@login_required
@profile_active_required
def view_list():
    form = SearchClientForm()
    search = (request.args.get("search", "False") in ("true", "True"))
    search_data = {}
    if search:
        show_search = True
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
        clients = Client.get_by_user(current_user.id)
        show_search = current_user.get_config_force("show_searchbar_client", 0).as_int() == 1

    return render_template("client/list.html", clients=clients, search=search, search_data=search_data, show_search=show_search, form=form)


@client_bp.route("/list/search/", methods=["POST"])
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


@client_bp.route("/details/<token>/", methods=["GET"])
@login_required
@profile_active_required
def details(token=None):
    form = NoteForm()
    client = Client.get_by_token(token)
    if client is None:
        abort(404)

    if not client.id_user == current_user.id:
        abort(404) 

    return render_template("client/details.html", client=client, token=token, form=form)

@client_bp.route("/list-sales/<token>/", methods=["GET"])
@login_required
@profile_active_required
def list_sales(token=None):
    form = NoteForm()
    client = Client.get_by_token(token)
    if client is None:
        abort(404)

    if not client.id_user == current_user.id:
        abort(404) 
        
    resume = request.args.get("resume", None) in ("true", "True")
    by_unit = request.args.get("by_unit", "true") in ("true", "True")
        
    sales = client.get_sales()
    if resume:
        total = client.get_resume(sales)
    else:
        total = None

    form.note.data = client.note
    
    simple = int(request.args.get("simple", current_user.get_simple_mode()))
    if simple and False:
        html_file = "client/simple/list_sales.html"
    else:
        html_file = "client/list_sales.html"

    return render_template(html_file, client=client, token=token, sales=sales, total=total, by_unit=by_unit, form=form)


@client_bp.route("/resume/<token>/", methods=["GET"])
@login_required
@profile_active_required
def resume(token=None):
    form = NoteForm()
    client = Client.get_by_token(token)
    if client is None:
        abort(404)

    if not client.id_user == current_user.id:
        abort(404) 
        
    by_unit = request.args.get("by_unit", "true") in ("true", "True")
        
    sales = client.get_sales()
    total = client.get_resume(sales)

    form.note.data = client.note
    
    simple = int(request.args.get("simple", current_user.get_simple_mode()))
    if simple and False:
        html_file = "client/simple/resume.html"
    else:
        html_file = "client/resume.html"

    return render_template(html_file, client=client, token=token, sales=sales, total=total, by_unit=by_unit, form=form)




@client_bp.route("/discard/<token>/", methods=["GET"])
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



@client_bp.route("/note/set/<token>/", methods=["POST"])
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





@client_bp.route("/p/update/<token>/", methods=["GET", "POST"])
@client_bp.route("/p/update/<token>/pr/<product_token>/", methods=["GET", "POST"])
@client_bp.route("/p/update/<token>/ls/<list_sale_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def product_add(token=None, product_token=None, list_sale_token=None):
    form = AddClientProductForm()
    
    client = Client.get_by_token(token)
    if client is None:
        abort(404)

    if not client.id_user == current_user.id:
        abort(404) 

    mode = "add"
    show_finish = True
    sale = None
    product = None
    error = 0

    if list_sale_token is not None:
        sale = ListSales.get_by_token(list_sale_token)
        if sale is None or not sale.id_group_sale == client.id_group_sale:
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
                    sale = ListSales.get_by_price_cost_and_group_sale(id_group_sale=client.id_group_sale, id_cost=cost.id, price=int(price))
                    if sale is not None:
                        sale.quantity += quantity
                    else:
                        sale = ListSales(id_group_sale=client.id_group_sale, id_cost=cost.id, price=int(price), quantity=int(quantity))
                
                else:
                    sale.quantity = quantity
                    sale.price = price

                sale.save()

                cl_sale = ClientSale.get_by_list_sales(sale)
                if cl_sale is None:
                    cl_sale = ClientSale(id_list_sales=sale.id, profit_paid=False)
                    cl_sale.save()

                next_page = request.form.get('next', None)
                if not next_page or url_parse(next_page).netloc == "":
                    next_page = url_for('client.view_list')

                    if form.submit.data:
                        next_page = url_for('client.product_add', token=token)

                    elif token is not None:
                        next_page = url_for('client.list_sales', token=token)

                return redirect(next_page)

    if product is not None:
        product_token = product.token
        p_cost = product.get_cost(date=None)
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
        "client/add_product.html", form=form, mode=mode, show_finish=show_finish,\
            client=client, product=product, sale=sale, error=error
    )




@client_bp.route("/discard/<token>/ls/<list_sale_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def product_delete_sale(token=None, list_sale_token=None):
    form = None
    
    client = Client.get_by_token(token)
    if client is None:
        abort(404)

    if not client.id_user == current_user.id:
        abort(404) 

    sale = None
    if list_sale_token is not None:
        sale = ListSales.get_by_token(list_sale_token)
        if sale is None or not sale.id_group_sale == client.id_group_sale:
            abort(404)

        cl_sale = sale.get_client_sale()
        if cl_sale is not None:
            cl_sale.delete()

        sale.delete()

    return redirect(url_for("client.list_sales", token=token))


@client_bp.route("/details/<token>/ls/<list_sale_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def product_sale_details(token=None, list_sale_token=None):
    form = None
    
    client = Client.get_by_token(token)
    if client is None or not client.id_user == current_user.id:
        abort(404) 

    sale = None
    cl_sale = None
    product = None
    cost = None
    if list_sale_token is not None:
        sale = ListSales.get_by_token(list_sale_token)
        if sale is None or not sale.id_group_sale == workday.id_group_sale:
            abort(404)

        cost = sale.cost
        product = cost.product
        cl_sale = sale.get_client_sale()


    
    profiles = Profile.get_by_user(current_user.id, only_active=True)

    return render_template(
        "client/sale_details.html", client=client, product=product, cost=cost, sale=sale, cl_sale=cl_sale, profiles=profiles
    )
