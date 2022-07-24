"""Product routes"""
import logging
import math
import random

from app.models.models import Cost, Product, Profile
from app.utils.decorators import profile_active_required
from app.utils.functions import analyze_int_fields, calculate, nice_price
from flask import abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import product_bp
from .forms import AddProductForm, SearchProductForm, ToolsNicePriceForm

logger = logging.getLogger(__name__)

@product_bp.route("/update/", methods=["GET", "POST"])
@product_bp.route("/update/<token>/", methods=["GET", "POST"])
@product_bp.route("/w/update/<workday_token>/", methods=["GET", "POST"])
@product_bp.route("/w/update/<token>/<workday_token>/", methods=["GET", "POST"])
@product_bp.route("/s/update/<shoppingday_token>/", methods=["GET", "POST"])
@product_bp.route("/s/update/<token>/<shoppingday_token>/", methods=["GET", "POST"])
@product_bp.route("/c/update/<client_token>/", methods=["GET", "POST"])
@product_bp.route("/c/update/<token>/<client_token>/", methods=["GET", "POST"])
@login_required
@profile_active_required
def add(token=None, workday_token=None, shoppingday_token=None, client_token=None):
    form = AddProductForm()

    mode = "add"
    show_finish = True
    product = None
    error = 0

    if form.validate_on_submit():
        name = form.product.data
        description = form.description.data
        # 'cost, extra_cost, price' verification
        try:
            cost = calculate(form.cost.data)
            if cost <= 0:
                error += 1
                form.cost.errors.append("Costo mínimo: $1")

            try:
                if (len(form.extra_cost.data) >= 1):
                    extra_cost = calculate(form.extra_cost.data)
                else:
                    extra_cost = 0

                if extra_cost < 0:
                    error += 1
                    form.extra_cost.errors.append("Costo extra mínimo: $0")

                try:
                    default_price = calculate(form.default_price.data)
                    if default_price < (cost+extra_cost):
                        error += 1
                        form.default_price.errors.append(f"No puede usarse un precio de venta menor que el costo.")
                        
                except BaseException:
                    error += 1
                    form.default_price.errors.append("Verifique el número ingresado.")

            except BaseException:
                error += 1
                form.extra_cost.errors.append("Verifique el número ingresado.")

        except BaseException:
            error += 1
            form.cost.errors.append("Verifique el número ingresado.")

        # 'quantity' verification
        try:
            quantity = calculate(form.quantity.data)

        except BaseException:
            error += 1
            form.quantity.errors.append("Verifique el número ingresado.")

        new = int(form.new.data)
        active = int(form.status.data)

        if error == 0:
            product, p_cost = save_product(
                name=name,
                description=description,
                default_price=default_price,
                cost=cost,
                extra_cost=extra_cost,
                quantity=quantity,
                new=new,
                active=active,
                token=token
            )

        
            next_page = request.form.get('next', None)
            if not next_page or url_parse(next_page).netloc == "":
                next_page = url_for('product.add')
                if workday_token is not None:
                    next_page = url_for('workday.product_add',
                        token=workday_token,
                        product_token=product.token
                    )

                elif shoppingday_token is not None:
                    next_page = url_for("shoppingday.product_add",
                        token=shoppingday_token,
                        product_token=product.token
                    )

                elif client_token is not None:
                    next_page = url_for("client.product_add",
                        token=client_token,
                        product_token=product.token
                    )

                elif token is not None and not (request.args.get("show_continue", "false")  in ("true", "True")):
                    next_page = url_for('product.details', token=token)

                elif form.submit_and_finish.data:
                    next_page = url_for('product.view_list')

            return redirect(next_page)

    else:
        form.quantity.data = str(1)
        if token is not None:
            product = Product.get_by_token(token)
            if product is None or not product.id_user == current_user.id:
                abort(404)
                
            cost = product.get_current_cost()

            form.product.data = product.name
            form.description.data = product.description
            form.quantity.data = str(0)
            form.new.data = str(int(product.new))
            form.status.data = str(int(product.active))
            
            form.cost.data = str(cost.cost)
            form.extra_cost.data = str(cost.extra_cost)
            form.default_price.data = str(cost.get_price())
            mode = "edit"

    if token or workday_token or shoppingday_token:
        show_finish = False

        if not (workday_token or shoppingday_token):
            show_finish = (request.args.get("show_continue", "false")  in ("true", "True"))
        
    return render_template(
        "product/add.html", form=form, mode=mode, product=product, error=error, token=token,\
            show_finish=show_finish, workday_token=workday_token, shoppingday_token=shoppingday_token,\
                client_token=client_token)


@product_bp.route("/list/details/", methods=["GET"])
@login_required
@profile_active_required
def list_details():
    products = Product.get_by_user(current_user.id)
    total = {
        'stock': 0,
        'products': 0,
        'cost': 0,
        'gain': 0,
        'price': 0,
        'sales': 0,
        'products_dont_show': 0,
        'available_products': 0,
        'sales_price': 0,
        'sales_cost': 0,
        'sales_gain': 0,
        'available_new': 0,
        'available_used': 0,
        'available_new_stock': 0,
        'available_used_stock': 0,
        'new': 0,
        'used': 0,
        'new_stock': 0,
        'used_stock': 0,
    }

    for product in products:
        sales = product.get_sales()
        stock = product.get_stock(sales=sales)
        total['products'] += 1
        if product.new:
            total['new'] += 1
            total['new_stock'] += stock
        else:
            total['used'] += 1
            total['used_stock'] += stock
        
        if stock >= 1:
            cost = product.get_current_cost()
            total['stock'] += stock
            total['cost'] += stock * cost.get_real_cost()
            total['gain'] += stock * product.get_gain()
            total['price'] += stock * cost.get_price()
            if product.active:
                total['available_products'] += int(stock >= 1)
            else:
                total['products_dont_show'] += 1

            if product.new:
                total['available_new'] += 1
                total['available_new_stock'] += stock
            else:
                total['available_used'] += 1
                total['available_used_stock'] += stock
        else:
            total['products_dont_show'] += 1

        for sale in sales:
            total['sales_price'] += sale.price * sale.quantity
            total['sales_cost'] += sale.cost.get_real_cost() * sale.quantity

        # "get_stock = total_stock - total_sales" then "sales = total_stock - get_stock"
        total['sales'] += product.stock - stock    
    
    total['sales_gain'] = total['sales_price'] - total['sales_cost']

    simple = int(request.args.get("simple", current_user.get_simple_mode()))
    if simple:
        html_file = "product/simple/list_details.html"
    else:
        html_file = "product/list_details.html"

    return render_template(html_file, products=products, total=total)


@product_bp.route("/list/", methods=["GET"])
@product_bp.route("/search-compare/list/<compare_token>/", methods=["GET"])
@product_bp.route("/search-workday/list/<workday_token>/", methods=["GET"])
@product_bp.route("/search-shoppingday/list/<shoppingday_token>/", methods=["GET"])
@product_bp.route("/search-client/list/<client_token>/", methods=["GET"])
@login_required
@profile_active_required
def view_list(show_all=None, compare_token=None, workday_token=None, shoppingday_token=None, client_token=None):
    show_all = (request.args.get('show_all', current_user.get_config_force("show_all_products", 0).as_int()) in ("true", "True", 1))
    search = (request.args.get("search", None) in ("true", "True"))
    warnings = (request.args.get("warnings", None) in ("true", "True"))
    form = SearchProductForm()
    search_data = {}

    show_search = False

    if search == False:
        # Obtener configuraciones:
        try:
            split_by = current_user.get_config_force("product_split_by", 50).as_int()
        except BaseException:
            split_by = 50
            current_user.set_config("product_split_by", 50)

        try:
            show_search = current_user.get_config_force("show_searchbar_product", 0).as_int() == 1
            if show_search:
                split_by = 300

        except BaseException:
            show_search = False
            current_user.set_config("show_searchbar_product", 0)

        # Obtener productos
        cantidad = Product.get_count_by_user(current_user.id, only_active=not show_all)
       
        page_max = int(math.ceil(cantidad / split_by))
        try:
            page = int(request.args.get('page'))

        except (ValueError, TypeError):
            page = 1

        # if page > page_max:
        #     abort(404)

        page = max(1, page)
        products = Product.get_by_user(current_user.id, limit=split_by, offset=split_by*(page-1), only_active=not show_all)
    else:
        page = 1
        page_max = 1
        min_price = int(request.args.get("min_price", "0"))
        max_price = int(request.args.get("max_price", "1"+"0"*50))

        min_cost = int(request.args.get("min_cost", "0"))
        max_cost = int(request.args.get("max_cost", "1"+"0"*50))

        min_profit = int(request.args.get("min_profit", "0"))
        max_profit = int(request.args.get("max_profit", "1"+"0"*50))

        min_stock = int(request.args.get("min_stock", "0"))
        max_stock = int(request.args.get("max_stock", "1"+"0"*50))

        min_sales = int(request.args.get("min_sales", "0"))
        max_sales = int(request.args.get("max_sales", "1"+"0"*50))

        name = (request.args.get("name", None))

        advanced = False
        for _name in ("min_cost", "min_profit", "min_stock", "min_sales", "max_cost", "max_profit", "max_stock", "max_sales"):
            if not request.args.get(_name, None) is None:
                advanced = True
                break
        
        search_data = {'advanced': advanced, 'name': name, 'max_price': max_price, 'min_price': min_price}
        total = 0
        products = []
        for product in Product.get_by_user(current_user.id):
            total += 1
            cost = product.get_current_cost()
            price = cost.get_price()
            rcost = cost.get_real_cost()
            profit = price-rcost
            stock = product.get_stock()
            sales = product.get_sales_count()

            if price >= min_price and price <= max_price and \
                rcost >= min_cost and rcost <= max_cost and \
                    profit >= min_profit and profit <= max_profit and \
                        stock >= min_stock and stock <= max_stock and \
                            sales >= min_sales and sales <= max_sales:

                if name is not None:
                    if name.upper() in product.get_name().upper():
                        products.append(product)
                        continue
                else:
                    products.append(product)
                    continue


        search_data['results'] = len(products)
        search_data['total'] = total

    if workday_token is not None:
        compare_token = None
        shoppingday_token = None
        client_token = None

    elif shoppingday_token is not None:
        compare_token = None
        client_token = None

    elif client_token is not None:
        compare_token = None

    return render_template(
        "product/list.html", products=products, page=page, page_max=page_max, show_all=show_all, compare_token=compare_token, client_token=client_token,
        search=search, search_data=search_data, form=form, workday_token=workday_token, shoppingday_token=shoppingday_token, warnings=warnings,
        show_search=show_search,
    )


@product_bp.route("/list/search/", methods=["POST"])
@product_bp.route("/search-compare/list/search/<compare_token>/", methods=["POST"])
@product_bp.route("/search-workday/list/search/<workday_token>/", methods=["POST"])
@product_bp.route("/search-shoppingday/list/search/<shoppingday_token>/", methods=["POST"])
@product_bp.route("/search-client/list/search/<client_token>/", methods=["POST"])
@login_required
@profile_active_required
def list_search(compare_token=None, workday_token=None, shoppingday_token=None, client_token=None):
    form = SearchProductForm()
    error = 0

    if form.validate_on_submit():
        # Name
        if form.name.data:
            name = form.name.data
        else:
            name = None

        # Price
        min_price, error = analyze_int_fields(form.min_price, None)
        max_price, error = analyze_int_fields(form.max_price, None)
        # Cost
        min_cost, error = analyze_int_fields(form.min_cost, None)
        max_cost, error = analyze_int_fields(form.max_cost, None)
        # Profit
        min_profit, error = analyze_int_fields(form.min_profit, None)
        max_profit, error = analyze_int_fields(form.max_profit, None)
        # Stock
        min_stock, error = analyze_int_fields(form.min_stock, None)
        max_stock, error = analyze_int_fields(form.max_stock, None)
        # Sales
        min_sales, error = analyze_int_fields(form.min_sales, None)
        max_sales, error = analyze_int_fields(form.max_sales, None)

        # ShowAll
        show_all = True

    if error == 0:
        return redirect(
            url_for(
                "product.view_list", search='true', compare_token=compare_token, name=name, min_price=min_price, max_price=max_price, show_all=str(show_all).lower(),
                min_cost=min_cost, max_cost=max_cost, min_profit=min_profit, max_profit=max_profit, min_stock=min_stock, max_stock=max_stock, min_sales=min_sales, max_sales=max_sales,
                workday_token=workday_token, shoppingday_token=shoppingday_token, client_token=client_token
            )
        )

    else:
        return view_list(compare_token=compare_token, workday_token=workday_token, shoppingday_token=shoppingday_token, client_token=client_token)
            

@product_bp.route("/details/<token>/", methods=["GET"])
@login_required
@profile_active_required
def details(token=None):
    product = Product.get_by_token(token)
    
    if product is None:
        abort(404)

    if not product.id_user == current_user.id:
        abort(404)   
    
    cost = product.get_current_cost()
    sales = product.get_sales_sorted()

    simple = int(request.args.get("simple", current_user.get_simple_mode()))
    if simple:
        html_file = "product/simple/details.html"
    else:
        html_file = "product/details.html"

    return render_template(html_file, product=product, cost=cost, sales=sales, token=token)


@product_bp.route("/compare/<token1>/with/<token2>/", methods=["GET"])
@login_required
@profile_active_required
def compare(token1=None, token2=None):
    product1 = Product.get_by_token(token1)
    
    if product1 is None or not product1.id_user == current_user.id:
        abort(404)

    product2 = Product.get_by_token(token2)
    
    if product2 is None or not product2.id_user == current_user.id:
        abort(404)   
    
    cost1 = product1.get_current_cost()
    cost2 = product2.get_current_cost()

    simple = int(request.args.get("simple", current_user.get_simple_mode()))
    if simple:
        html_file = "product/simple/compare.html"
    else:
        html_file = "product/compare.html"

    return render_template(html_file,
            product1=product1, product2=product2, cost1=cost1, cost2=cost2, token1=token1, token2=token2
        )



@product_bp.route("/tools/niceprice/", methods=["GET", "POST"])
@login_required
@profile_active_required
def tools_nice_price():
    form = ToolsNicePriceForm()
    show_all_levels = (request.args.get("show_all", "false")  in ("true", "True"))
    product_token = request.args.get("token", "")

    result = False
    cost = 0
    extra_cost = 0
    rcost = None
    new = None
    price = None
    gain = None
    profiles_number = max(1, Profile.get_count_by_user(current_user.id, only_active=True))
    error = 0
    percent = False
    is_valid_form = form.validate_on_submit()
    url_chart = None
    is_user_price = False

    if request.args.get("cost", None) is not None and not is_valid_form:
        form.cost.data = request.args.get("cost", "100")
        form.extra_cost.data = request.args.get("extra", "0")
        form.price.data = request.args.get("price", "")
        form.new.data = str(int(request.args.get("new", "true")  in ("true", "True")))
        form.submit.data = True
        is_valid_form = True
    
    elif len(product_token) >= 1:
        product = Product.get_by_token(product_token)

        if product is None or not product.id_user == current_user.id:
            return redirect(url_for("product.tools_nice_price"))  # Para no mostrar errores, directamente redirijo a la página de nice price.

        p_cost = product.get_current_cost()
        form.cost.data = str(p_cost.cost)
        form.extra_cost.data = str(p_cost.extra_cost)
        form.price.data = str(p_cost.get_price())
        form.new.data = str(int(product.new))
        form.submit.data = True
        is_valid_form = True

    if is_valid_form:
        result = True
        new = int(form.new.data)

        if form.show_all.data:
            show_all_levels = int(form.show_all.data)

        # 'cost, extra_cost, price' verification:
        try:
            cost = calculate(form.cost.data)

            if cost < 1:
                error += 1
                form.cost.errors.append("Costo mínimo: $1")

            try:
                if len(form.extra_cost.data):
                    extra_cost = calculate(form.extra_cost.data)
                else:
                    extra_cost = 0

                if extra_cost < 0:
                    error += 1
                    form.extra_cost.errors.append("Costo extra mínimo: $0")

                rcost = cost + extra_cost
                try:
                    if len(form.price.data):
                        is_user_price = True

                        price_data = form.price.data
                        price = calculate(price_data, {'cost': rcost})
                        if percent:
                            price = int(rcost * (1+(price/100)))
                        
                        if price < (rcost):
                            form.price.errors.append("El precio no puede ser menor que el costo.")
                            form.price.errors.append(f"Costo Total: ${rcost}")
                            
                    else:
                        price = nice_price.get_price(rcost, new, level=3)
                        

                    gain = price-rcost

                except BaseException:
                    error += 1
                    form.price.errors.append("Verifique el número ingresado.")

            except BaseException:
                error += 1
                form.extra_cost.errors.append("Verifique el número ingresado.")

        except BaseException:
            error += 1
            form.cost.errors.append("Verifique el número ingresado.")

        
        if error >= 1:
            result = None
            rcost = None
            new = None
            price = None
            gain = None
            cost = 0
            extra_cost = 0
            is_user_price = False
    
    else:
        form.new.data = "1"
        
    return render_template("product/tool_nice_price.html",
        profiles_number=profiles_number,
        is_user_price=is_user_price,
        form=form,
        result=result,
        rcost=rcost,
        cost=cost,
        extra_cost=extra_cost,
        new=new,
        price=price,
        gain=gain, 
        error=error, 
        show_all_levels=show_all_levels
    )


@product_bp.route("/discard/<token>/", methods=["GET"])
@login_required
@profile_active_required
def discard(token=None):
    product = Product.get_by_token(token)
    if product is None or not product.id_user == current_user.id:
        abort(404) 

    if product.can_be_deleted():
        product.delete_product_and_costs()
        
    return redirect(url_for("product.view_list"))


@product_bp.route("/test/add/<int:number>/<name>/")
@login_required
@profile_active_required
def test_add(number, name):
    for i in range(1, 1+int(number)):
        price = random.randint(10, 80)*10
        new = random.randint(0, 10)%2
        product = Product(
            id_user=current_user.id,
            name=f"{name} {i:04d}",
            description="",
            new=new,
            stock=random.randint(0, 50),
            active=True
        )
        product.save()

        p_cost = Cost(cost=random.randint(price*0.3, price*0.8), extra_cost=10*new, price=price, id_product=product.id)
        p_cost.save()

    return redirect(url_for("product.view_list"))


def save_product(name, description, default_price, cost, extra_cost, quantity=1, new=1, active=1, token="", hidden_token=None):
    # Crear el producto si no existe ninguno con el nombre ingresado:
    product = None
    p_cost = None
    if token:
        product = Product.get_by_token(token)
        if not product.id_user == current_user.id:
            product = None
    
    if not product:
        product = Product.get_by_name(name, current_user.id)

    if product:
        product.name = name.upper()
        product.description = description
        stock = product.get_stock()
        product.set_stock(quantity)
        product.new = new
        product.active = active

        p_cost = product.get_current_cost()
        if not (p_cost.cost == cost and p_cost.extra_cost == extra_cost and p_cost.price == default_price):
            p_cost = Cost(cost=cost, extra_cost=extra_cost, price=default_price, id_product=product.id)
            p_cost.save()
            

        product.save()

    else:
        product = Product(
            id_user=current_user.id,
            name=name,
            description=description,
            new=new,
            stock=max(0, quantity),
            active=active,
        )
        product.save()

        p_cost = Cost(cost=cost, extra_cost=extra_cost,  price=default_price, id_product=product.id)
        p_cost.save()

    return product, p_cost


