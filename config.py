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
	MAIL_USE_SSL = False
	MAIL_SUBJECT_PREFIX = '[Tool TL;DR]'

	ADMIN = os.environ.get('TOOL_TLDR_ADMIN')

	CACHE_TYPE = "filesystem"
	CACHE_DIR = "/tmp/website_cache"
	CACHE_DEFAULT_TIMEOUT = 50

	EDITS_PER_PAGE = 20
	ALTS_PER_LIST = 10

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'app-dev.db')


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


config = {
	'dev': DevelopmentConfig,
	'test': TestingConfig,
	'prod': ProductionConfig,
	'default': DevelopmentConfig
}