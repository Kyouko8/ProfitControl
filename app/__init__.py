import logging

import stripe
from flask import Flask, render_template
from flask_htmlmin import HTMLMIN
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from werkzeug.exceptions import HTTPException

from .instance import configuration

VERSION = "0.7 alpha"

csrf = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
htmlmin = HTMLMIN()

stripe = stripe

offline = False

def configure_logging():
    FORMAT = """[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)s]    %(message)s\n"""
    logging.basicConfig(format=FORMAT)


def create_app():
    app = Flask(__name__)
    app.config.from_object(configuration.Production)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicie sesión para acceder a esta sección"

    stripe.api_key = app.config["STRIPE_API_KEY"]

    db.init_app(app)
    csrf.init_app(app)
    htmlmin.init_app(app)

    # Registrar los BP:
    from .blueprint import BLUEPRINTS
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .api import api_bp
    app.register_blueprint(api_bp)

    from .download import download_bp
    app.register_blueprint(download_bp)

    from .public import public_bp
    app.register_blueprint(public_bp)

    from .payment import payment_bp
    app.register_blueprint(payment_bp)

    register_error_handler(app)
    configure_logging()

    return app

# Control Errors
def register_error_handler(app):
    @app.errorhandler(Exception)
    def error_handler(e):
        logging.error(f"{type(e).__name__} -> {e}")
        code = 500
        if isinstance(e, HTTPException):
            code = e.code

        return render_template("errors/error.html", error_code=str(code)), int(code)
