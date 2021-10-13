"""Name routes"""
import logging
import os
import json
import datetime
from flask import render_template, current_app, url_for, request, abort, redirect
from flask_login import current_user, login_required

from . import name_bp
from app.models import Product

logger = logging.getLogger(__name__)


@name_bp.route("/index.html")
@login_required
def index():
    return render_template("_/index.html")
