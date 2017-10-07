import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
	SQLALCHEMY_TRACK_MODIFICATIONS = True

	WHOOSH_BASE = os.path.join(basedir, 'search.db')
	WTF_CSRF_ENABLED = True

	RECAPTCHA_USE_SSL = True
	RECAPTCHA_PUBLIC_KEY = "6Lfn1icUAAAAAMefI3wT1KHDA6fcgThmbVMqv4MB"
	RECAPTCHA_PRIVATE_KEY = "6Lfn1icUAAAAAFjb_GazZxvWwQqEam7FpkCiUALA"

	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or "tooltldr@gmail.com"
	MAIL_SENDER = os.environ.get('MAIL_SENDER') or "tooltldr@gmail.com"
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "mrdtwuqkliivoxvv"
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_SUBJECT_PREFIX = '[Tool TL;DR]'

	ADMIN = os.environ.get('TOOL_TLDR_ADMIN')

	CACHE_TYPE = "filesystem"
	CACHE_DIR = "/tmp/website_cache"
	CACHE_DEFAULT_TIMEOUT = 50

	EDITS_PER_PAGE = 20
	ALTS_PER_LIST = 10

	BLOCKING_USERS = True

	SSLIFY_PERMANENT = True

	SECURITY_HEADERS = {
		"X-Frame-Options": "DENY",
		"X-Xss-Protection": "1; mode=block",
		"X-Content-Type-Options": "nosniff",
		"Referrer-Policy": "no-referrer-when-downgrade"
	}

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'app-dev.db')
	TEMPLATES_AUTO_RELOAD = True


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'app-test.db')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'app.db')

	# MySQL fix
	SQLALCHEMY_POOL_SIZE = 100
	SQLALCHEMY_POOL_RECYCLE = 280

	SECURITY_HEADERS = {
		"Content-Security-Policy": "default-src 'none'; script-src 'self' https://ajax.googleapis.com; img-src https:; style-src 'self'; connect-src 'self'",
		"X-Frame-Options": "DENY",
		"X-Xss-Protection": "1; mode=block",
		"X-Content-Type-Options": "nosniff",
		"Referrer-Policy": "no-referrer-when-downgrade"
	}


config = {
	'dev': DevelopmentConfig,
	'test': TestingConfig,
	'prod': ProductionConfig,
	'default': DevelopmentConfig
}