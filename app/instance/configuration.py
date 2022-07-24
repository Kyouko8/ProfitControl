import os


class Config:
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	SESSION_COOKIE_SECURE = True
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SAMESITE = 'Lax'

	MINIFY_HTML = True

class Production(Config):
	PATH = "/var/www/profitcontrol/ProfitControl"
	DEBUG = False
	SQLALCHEMY_DATABASE_URI = None
	SECRET_KEY = os.environ.get('PC_SECRET_KEY')

	SQLALCHEMY_DATABASE_URI = f"sqlite:///{PATH}/app/.database.sqlite3"

	STRIPE_WEBHOOK_SECRET = os.environ.get('PC_STRIPE_WEBHOOK_SECRET')
	STRIPE_API_KEY = os.environ.get('PC_STRIPE_API_KEY')

	DOWNLOAD_FOLDER = f'{PATH}/download/files'
	UPLOAD_FOLDER = f'{PATH}/upload/files'

class Development(Config):
	PATH = os.path.abspath(f"{ os.path.abspath(os.getcwd()) }")
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = f"sqlite:///{PATH}/app/.database.sqlite3"
	SECRET_KEY = "1234"

	STRIPE_WEBHOOK_SECRET = "whsec_37d8dfa8126d6786d0468c8b70fc280c605cc940209a1c1374d214c61bd9b5fb"
	STRIPE_API_KEY        = "sk_test_kZp1kdgQbOxszws5vvCilLrb0001bTiENk"

	DOWNLOAD_FOLDER = f'{PATH}/download/files'
	UPLOAD_FOLDER = f'{PATH}/upload/files'
	