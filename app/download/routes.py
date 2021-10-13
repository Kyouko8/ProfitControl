"""Download routes"""
import logging
import os
import json
import datetime
import io
from flask import render_template, send_file, send_from_directory, current_app
from flask_login import current_user, login_required

from . import download_bp
from . import uploading 
from app.models import Product

logger = logging.getLogger(__name__)

DOWNLOAD_ROUTE_1 = "dwn"  # Use this for Normal Downloads
DOWNLOAD_ROUTE_2 = "alt"  # Use this for Alternative Method Downloads

def get_memory_file_to_download(content):
    if not isinstance(content, bytes):
        content = str(content).encode()

    memory_file = io.BytesIO()
    memory_file.write(content)
    memory_file.seek(0)

    return memory_file

@download_bp.route("/download/index.html")
@login_required
def index():
    return render_template("download/index.html")


@download_bp.route(f"/download/{DOWNLOAD_ROUTE_1}/<path:filename>")
@login_required
def dwn_file(filename):
    return send_from_directory(current_app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=True)


@download_bp.route(f"/download/{DOWNLOAD_ROUTE_2}/<path:filename>")
@login_required
def alt_file(filename):
    path = os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename)
    return send_file(path, attachment_filename="alt_"+os.path.basename(path))


def prepare_dict_products(only_active = False):
    if current_user.is_authenticated:
        data = []
        products = Product.get_by_user(current_user.id, only_active=only_active)
        for product in products:
            data.append(product.as_dict())

        return data
    else:
        return None

    
@download_bp.route(f"/download/json/products/")
@download_bp.route(f"/download/json/products/<int:indent>/")
@login_required
def json_products(indent=None):
    content = prepare_dict_products()
    if content is None:
        return abort(403)

    filecontent = get_memory_file_to_download(json.dumps(content, indent=indent))
    filename = f"Products-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')}-{current_user.username}.profitjson"

    return send_file(
        filecontent,
        as_attachment=True,
        attachment_filename=filename,
        mimetype='text/json'
    )


