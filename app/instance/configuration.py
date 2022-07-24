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
	SECRET_KEY = "HEzjUKv1Ftg01Nz6nqHZcgiuPDQcikISCA0smTk6ZgBLljCZClldfdZw-KTdnkra0ea1O1aBHSbgu0ZWTM1I9w"#os.environ.get('SECRET_KEY')

	SQLALCHEMY_DATABASE_URI = f"sqlite:///{PATH}/app/.database.sqlite3"

	STRIPE_WEBHOOK_SECRET = "whsec_zfZOhz6CQLvQeB0bEfi4OCjLMok5SfXF"#os.environ.get('STRIPE_WEBHOOK_SECRET')
	STRIPE_API_KEY = "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"#os.environ.get('STRIPE_API_KEY')

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
	