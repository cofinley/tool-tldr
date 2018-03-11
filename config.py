import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Wjqjll33tKq1dOtTJo3Sued129ohlSNf'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    WHOOSH_BASE = os.path.join(basedir, 'search.db')
    WTF_CSRF_ENABLED = True

    RECAPTCHA_USE_SSL = True
    RECAPTCHA_PUBLIC_KEY = os.environ.get("TOOLTLDR_RECAPTCHA_SITE_KEY")
    RECAPTCHA_PRIVATE_KEY = os.environ.get("TOOLTLDR_RECAPTCHA_SECRET_KEY")
    RECAPTCHA_DATA_ATTRS = {'bind': 'recaptcha-submit', 'callback': 'onRecaptchaSubmitCallback', 'size': 'invisible'}

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

    CSP = {}

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TOOLTLDR_DATABASE_URL_DEV')
    TEMPLATES_AUTO_RELOAD = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TOOLTLDR_DATABASE_URL_TEST')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TOOLTLDR_DATABASE_URL_PROD')

    # MySQL fix
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 280

    CSP = {
        "default-src": "'none'",
        "script-src": [
            "'self'",
            "https://ajax.googleapis.com",
            "https://cdnjs.cloudflare.com",
            "https://maxcdn.bootstrapcdn.com",
            "https://www.google.com/recaptcha/",
            "https://www.gstatic.com/recaptcha/"
        ],
        "img-src": "https:",
        "style-src": "'self' https://fonts.googleapis.com 'unsafe-inline'",
        "connect-src": "'self'",
        "font-src": "https://fonts.gstatic.com",
        "manifest-src": "'self'",
        "frame-src": "https://www.google.com/recaptcha/"
    }

config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
