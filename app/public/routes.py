"""Public routes"""
import logging
import random
import datetime

from app.functions import (process_form_data, add_decimal_mark, get_month_name, get_day_name, nice_price, percent,
                            get_progress_color, get_color)
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_required



from . import public_bp
from app.models import Product
from app import offline, VERSION

logger = logging.getLogger(__name__)



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
        'offline': offline.data,

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
    offline.data = True
    return redirect(url_for("public.index"))

@public_bp.route("/_cfg/online/")
def cfg_online():
    offline.data = False
    return redirect(url_for("public.index"))



@public_bp.route("/favicon.ico")
def fav_icon():
    return redirect(url_for("static", filename="img/flaticon.ico"))