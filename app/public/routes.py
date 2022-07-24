"""Public routes"""
import datetime
import logging
import random

from app import VERSION
from app.models.models import Product
from app.utils.functions import (add_decimal_mark, get_color, get_day_name,
                                 get_month_name, get_progress_color,
                                 nice_price, percent, process_form_data)
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import public_bp

logger = logging.getLogger(__name__)


class Offline:
    pass

@public_bp.app_context_processor
def functions():
    return {
        'VERSION': VERSION, 
        
        'len': len,
        'enumerate': enumerate,
        'datetime': datetime.datetime,
        'random': random,
        'process_form_data': process_form_data,
        'add_decimal_mark': add_decimal_mark,
        'f': lambda x, digits=0: add_decimal_mark(x, digits),
        'get_month_name': get_month_name,
        'get_day_name': get_day_name,
        'percent': percent,
        'get_progress_color': get_progress_color,
        'get_color': get_color,

        'nice_price': nice_price,

        'repr': repr,
        'abs': abs,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'tuple': tuple,
        'round': round,
        'min': min,
        'max': max,
        'range': range,
    }

@public_bp.route("/")
@public_bp.route("/index.html")
def index():    
    return render_template(f"public/index.html")

@public_bp.route("/home/")
@login_required
def home():
    if current_user.is_authenticated:
        products = Product.get_by_user(current_user.id)
    else:
        products = []

    return render_template("public/home.html", products=products)


@public_bp.route("/about/")
@public_bp.route("/about.html")
def about():
    return render_template("public/about.html")


@public_bp.route("/_cfg/offline/")
def cfg_offline():
    Offline().data = True
    return redirect(url_for("public.index"))

@public_bp.route("/_cfg/online/")
def cfg_online():
    Offline().data = False
    return redirect(url_for("public.index"))



@public_bp.route("/favicon.ico")
def fav_icon():
    return redirect(url_for("static", filename="img/flaticon.ico"))
