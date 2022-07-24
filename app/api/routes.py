"""API routes"""
import logging
import time

from app.models.models import (Client, ClientSale, ListSales, ListShopping,
                               Product, ShoppingDay, UserConfig, WorkDay)
from app.utils.functions import nice_price
from flask import make_response, render_template, request, url_for
from flask_login import current_user, login_required

from . import api_bp  # url_prefix = "/api"

logger = logging.getLogger(__name__)


@api_bp.route("/index.html")
def index():
    return render_template("api/index.html")



@api_bp.route("/user/config/set/", methods=["POST"])
@login_required
def set_config():
    time.sleep(1)
    user_id = int(request.get_json()["user_id"])
    key = request.get_json()["config"]
    value = request.get_json()["value"]
    status = 200

    if not user_id == current_user.id:
        status = 404
    
    else:
        config = UserConfig.get_by_name(key, user_id)
            
        if config is None:
            config = UserConfig(id_user=current_user.id, key=key, value=value)
                
        config.value = value
        config.save()

    return make_response({}, status)



@api_bp.route("/search/product/", methods=["POST"])
@login_required
def search_product():
    time.sleep(1)
    
    searched_name = request.get_json()["product_name"].upper().strip()
    workday_token = request.get_json().get("workday_token", "None")
    shoppingday_token = request.get_json().get("shoppingday_token", "None")
    client_token = request.get_json().get("client_token", "None")
    url_address_type = request.get_json()["url_address_type"]
    try:
        page = int(request.get_json()['page'])
    except BaseException:
        page = 1

    try:
        limit = int(request.get_json()['limit'])
    except BaseException:
        limit = 7

    page = max(1, page)
    limit = min(50, max(5, limit))
    if workday_token == "None":
        workday_token = None

    if shoppingday_token == "None":
        shoppingday_token = None

    if client_token == "None":
        client_token = None

    products = Product.get_by_name_advanced(searched_name, current_user.id, limit=limit+1,  offset=limit*max(0, page-1))
    result = []

    if url_address_type == "product":
        for product in products:
            if len(result) < limit: #Limit to 7 by default
                dic = {
                    "name": product.get_name(),
                    "url": url_for(
                        "product.add",
                        token=product.token,
                        workday_token=workday_token,
                        shoppingday_token=shoppingday_token,
                        client_token=client_token,
                        show_continue="true"
                    )
                }

                result.append(dic)

    elif url_address_type == "workday":
        for product in products:
            if len(result) < limit: #Limit to 7 by default
                dic = {
                    "name": product.get_name(),
                    "url": url_for("workday.product_add", token=workday_token, product_token=product.token)
                }

                result.append(dic)

    elif url_address_type == "shoppingday":
        for product in products:
            if len(result) < limit: #Limit to 7 by default
                dic = {
                    "name": product.get_name(),
                    "url": url_for("shoppingday.product_add", token=shoppingday_token, product_token=product.token)
                }

                result.append(dic)

    elif url_address_type == "client":
        for product in products:
            if len(result) < limit: #Limit to 7 by default
                dic = {
                    "name": product.get_name(),
                    "url": url_for("client.product_add", token=client_token, product_token=product.token)
                }

                result.append(dic)
    
    has_next = (len(products) == (limit+1))
    

    info = {
        'has_next': has_next,
        'has_prev': page >= 2,
        'page': page,
        'limit': limit,
    }

    return make_response({"data": result, 'info': info}, 200)


@api_bp.route("/modify/product/stock/", methods=["POST"])
@login_required
def modify_product_stock():
    time.sleep(1)
    mode = request.get_json()["mode"] #add / remove (+ / -)
    product_token = request.get_json()["product_token"]

    value = None
    stock = -1
    product = Product.get_by_token(product_token)

    if product is None:
        status = 404

    elif product.id_user == current_user.id:
        if mode == "add":
            value = 1

        elif mode == "remove":
            value = -1

        if value is not None:
            product.set_stock(value, relative=True)
            stock = product.get_stock()
            product.save()
            status = 200

        else:
            status = 400

    else:
        status = 403

    return make_response({"new_stock": stock}, status)


@api_bp.route("/modify/w/sale/quantity/", methods=["POST"])
@login_required
def modify_workday_sales_quantity():
    time.sleep(1)
    mode = request.get_json()["mode"] #add / remove (+ / -)
    list_sale_token = request.get_json()["sale_token"]
    workday_token = request.get_json()["workday_token"]

    message = ""
    value = None
    error = False
    stock = -1
    workday = WorkDay.get_by_token(workday_token)
    data = {}

    if workday is None:
        status = 404

    elif workday.id_user == current_user.id:
        
        sale = ListSales.get_by_token(list_sale_token)
        
        if sale is None:
            status = 404
            
        elif sale.id_group_sale == workday.id_group_sale:
            if mode == "add":
                value = 1

            elif mode == "remove":
                value = -1

            if value is not None:
                stock = sale.quantity
                cost = sale.cost
                data['cost'] = cost.get_real_cost()
                data['price'] = sale.price
                data['name'] = cost.product.get_name()
                data['disable_add'] = False

                disponible = sale.cost.product.get_stock()
                if disponible == 0 and value >= 1:
                    message = "Insuficiente stock."
                    status = 200
                    error = True
                    data['disable_add'] = True
                else:
                    sale.quantity = max(1, sale.quantity + value)
                    stock = sale.quantity
                    sale.save()
                    message = f"Cantidad {value:+}"
                    disponible = sale.cost.product.get_stock()
                    data['disable_add'] = (disponible == 0)
                    status = 200
                    error = False

            else:
                status = 400
                error = True

        else:
            status = 400
            error = True

    else:
        status = 403
        error = True

    return make_response({"new_stock": stock, 'data': data, 'message': message, 'error': error}, status)


@api_bp.route("/modify/c/sale/quantity/", methods=["POST"])
@login_required
def modify_client_sales_quantity():
    time.sleep(1)
    mode = request.get_json()["mode"] #add / remove (+ / -)
    list_sale_token = request.get_json()["sale_token"]
    client_token = request.get_json()["client_token"]

    message = ""
    value = None
    error = False
    stock = -1
    client = Client.get_by_token(client_token)
    data = {}

    if client is None:
        status = 404

    elif client.id_user == current_user.id:
        
        sale = ListSales.get_by_token(list_sale_token)
        
        if sale is None:
            status = 404
            
        elif sale.id_group_sale == client.id_group_sale:
            if mode == "add":
                value = 1

            elif mode == "remove":
                value = -1

            if value is not None:
                stock = sale.quantity
                cost = sale.cost
                data['cost'] = cost.get_real_cost()
                data['price'] = sale.price
                data['name'] = cost.product.get_name()
                data['disable_add'] = False

                disponible = sale.cost.product.get_stock()
                if disponible == 0 and value >= 1:
                    message = "Insuficiente stock."
                    status = 200
                    error = True
                    data['disable_add'] = True
                else:
                    sale.quantity = max(1, sale.quantity + value)
                    stock = sale.quantity
                    sale.save()
                    message = f"Cantidad {value:+}"
                    disponible = sale.cost.product.get_stock()
                    data['disable_add'] = (disponible == 0)
                    status = 200
                    error = False

            else:
                status = 400
                error = True

        else:
            status = 400
            error = True

    else:
        status = 403
        error = True

    return make_response({"new_stock": stock, 'data': data, 'message': message, 'error': error}, status)


@api_bp.route("/modify/shopping/quantity/", methods=["POST"])
@login_required
def modify_shopping_quantity():
    time.sleep(1)
    mode = request.get_json()["mode"] #add / remove (+ / -)
    list_shopping_token = request.get_json()["shopping_token"]
    shoppingday_token = request.get_json()["shoppingday_token"]

    message = ""
    value = None
    error = False
    stock = -1
    shoppingday = ShoppingDay.get_by_token(shoppingday_token)
    data = {}

    if shoppingday is None:
        status = 404

    elif shoppingday.id_user == current_user.id:
        
        shopping = ListShopping.get_by_token(list_shopping_token)
        
        if shopping is None:
            status = 404
            
        elif shopping.id_group_shopping == shoppingday.id_group_shopping:
            if mode == "add":
                value = 1

            elif mode == "remove":
                value = -1

            if value is not None:
                cost = shopping.cost
                data['cost'] = cost.get_real_cost()
                data['price'] = cost.get_price()
                data['name'] = cost.product.get_name()
                data['disable_add'] = False

                shopping.quantity = max(1, shopping.quantity + value)
                stock = shopping.quantity
                shopping.save()
                message = f"Cantidad {value:+}"
                status = 200
                error = False

            else:
                status = 400
                error = True

        else:
            status = 400
            error = True

    else:
        status = 403
        error = True

    return make_response({"new_stock": stock, 'data': data, 'message': message, 'error': error}, status)



@api_bp.route("/tools/chart/niceprice/", methods=["POST"])
@login_required
def tools_chart_niceprice():
    time.sleep(1)
    status = 200
    message = "ok"

    try:
        cost = int(request.get_json()["cost"])
        extra_cost = int(request.get_json()["extra_cost"])
        price = int(request.get_json()["price"])
        new = int(request.get_json()["new"])
        is_user_price = int(request.get_json()["is_user_price"])
    except:
        status = 400 #BadRequest
        message = "Los datos enviados no son correctos. Se requiere un JSON de 4 parametros de tipo Integer."
    
    rcost = cost + extra_cost
    price = max(cost+extra_cost, price)
    profit = price-rcost

    result = {}

    def get_results():
        _result = {'prices': [], 'cost': [], 'extra_cost': []}

        _dat_prices = _result['prices']
        _dat_cost = _result['cost']
        _dat_extra_cost = _result['extra_cost']
        _user_level = None

        if is_user_price:
            name = f"Tu Precio (${int(price)})"
            level = nice_price.get_price_status(price, rcost, new, approximate=False)
            _user_level = int(level + 1)
            _dat_prices.append(
                {'x': _user_level, 'y': price-rcost, 'label': name, 'total': price}
            )
            _dat_cost.append(
                {'x': _user_level, 'y': cost, 'label': name, 'total': price}
            )
            _dat_extra_cost.append(
                {'x': _user_level, 'y': extra_cost, 'label': name, 'total': price}
            )

        
        name = f"Costo Total (${int(rcost)})"
        level = -1
        _dat_prices.append(
            {'x': level, 'y': 0, 'label': name, 'total': rcost}
        )
        _dat_cost.append(
            {'x': level, 'y': cost, 'label': name, 'total': rcost}
        )
        _dat_extra_cost.append(
            {'x': level, 'y': extra_cost, 'label': name, 'total': rcost}
        )

        for level in nice_price.get_levels_range():
            np_price = nice_price.get_price(rcost, new, level=level)
            name = f"{nice_price.get_level_name(level)} (${int(np_price)})"

            if _user_level is not None and level >= _user_level:
                level += 1

            _dat_prices.append(
                {'x': level, 'y': np_price-rcost, 'label': name, 'total': np_price}
            )
            _dat_cost.append(
                {'x': level, 'y': cost, 'label': name, 'total': np_price}
            )
            _dat_extra_cost.append(
                {'x': level, 'y': extra_cost, 'label': name, 'total': np_price}
            )

        return _result

    result['points'] = get_results()

    return make_response({"data": result, 'message': message}, 200)
