"""Download routes"""
import logging
import os
import json
import datetime
import io
from flask import render_template, request, url_for, redirect, current_app
from flask_login import current_user, login_required

from . import download_bp
from .forms import LoadJSONForm
from app.models.models import Product
from app.utils.functions import analyze_int_fields

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = ['json', 'profitjson', 'jsonprofit']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@download_bp.route("/product/upload/backup/", methods=['GET', 'POST'])
@login_required
def upload_backup_products():
    form = LoadJSONForm()

    errors = 0
    products_status = {'errors': 0, 'ok': 0, 'ok_ls': []}
    finish = False

    if form.validate_on_submit():
        user = current_user.id
        do_nothing_if_exists, errors = analyze_int_fields(form.if_exists)
        update_information, errors = analyze_int_fields(form.update)
        update_stock, errors = analyze_int_fields(form.stock)
        update_name, errors = analyze_int_fields(form.update_name)

        json_content = ""

        upload_file = request.files['upload_file']

        if upload_file.content_length >= 260*1048576: # File Size Max: 260MB 
            form.upload_file.errors.append("Tamaño máximo 256MB")
            errors += 1

        elif upload_file.filename == "":
            form.upload_file.errors.append("Seleccione un archivo")
            errors += 1

        elif not allowed_file(upload_file.filename):
            form.upload_file.errors.append("Solo se permiten archivos JSON y PROFITJSON. Estos se pueden obtener al descargar una copia de seguridad.")
            errors += 1

        if errors == 0:
            for stream in upload_file.stream:
                json_content += stream.decode()

            profit_json = json.loads(json_content)

            id_user = current_user.id

            for data in profit_json:
                try:
                    if update_name >= 1:
                        num = 1 + int(update_name == 2)
                        while Product.get_by_name(data['name'], id_user):
                            if num == 2 or update_name == 2:
                                data['name'] = "{name} ({num})".format(num=num, **data)
                            else:
                                if update_name == 1:
                                    data['name'] = "{name}@Copia".format(**data)
                                elif update_name == 3:
                                    data['name'] = "@{name}".format(**data)

                            num += 1
                        

                    product = Product.from_dict(data, id_user, do_nothing_if_exists=do_nothing_if_exists, update_stock=update_stock, update_information=update_information)
                    product.save()
                    products_status['ok'] += 1
                    products_status['ok_ls'].append(product)

                except (TypeError, AttributeError, ValueError):
                    products_status['errors'] += 1

            finish = True


    return render_template("upload/json.html", finish=finish, form=form, errors=errors, products_status=products_status)
    


            