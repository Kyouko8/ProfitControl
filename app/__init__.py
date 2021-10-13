import logging
from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
try:
    from flask_htmlmin import HTMLMIN
except ImportError:
    HTMLMIN = None

VERSION = "1.2.0.6 alpha"

csrf = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
if HTMLMIN is not None:
    htmlmin = HTMLMIN()

class _Offline():
    data = False

offline = _Offline


def configure_logging():
    FORMAT = """%(levelname)s:    %(message)s\n"""
    logging.basicConfig(format=FORMAT)


def create_app(minify=False, database=".data/database_1_2.sqlite3"):
    app = Flask(__name__)
    app.config['MINIFY_HTML'] = minify
    app.config['SECRET_KEY'] = 'SECRET_KEY'
    app.config['DOWNLOAD_FOLDER'] = 'download/files'
    app.config['UPLOAD_FOLDER'] = 'upload/files'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicie sesión para acceder a esta sección"

    db.init_app(app)
    csrf.init_app(app)
    if HTMLMIN is not None:
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

    register_error_handler(app)
    before_r(app)
    configure_logging()

    return app

# Control Errors
def register_error_handler(app):
    @app.errorhandler(403)  # Forbidden
    def show_error_403(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)  # Not Found
    def show_error_404(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)  # Server Error
    def show_error_500(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(429) # Too Many Requests
    def show_error_429(e):
        print("too many requests")
        return render_template("errors/500.html"), 429

def before_r(app):
    @app.before_request
    def before_request():
        pass
        # print(request.user_agent.platform)
