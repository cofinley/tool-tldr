import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('TOOLTLDR_SECRET_KEY')

    # Flask-SQLAlchemy
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Flask-WhooshAlchemyPlus
    WHOOSH_BASE = os.path.join(basedir, 'search.db')
    WTF_CSRF_ENABLED = True

    # Flask-WTF
    RECAPTCHA_USE_SSL = True
    RECAPTCHA_PUBLIC_KEY = os.environ.get("TOOLTLDR_RECAPTCHA_SITE_KEY")
    RECAPTCHA_PRIVATE_KEY = os.environ.get("TOOLTLDR_RECAPTCHA_SECRET_KEY")
    RECAPTCHA_DATA_ATTRS = {'bind': 'recaptcha-submit', 'callback': 'onRecaptchaSubmitCallback', 'size': 'invisible'}

    # Flask-Mail
    MAIL_USERNAME = os.environ.get('TOOLTLDR_MAIL_USERNAME')
    MAIL_SENDER = os.environ.get('TOOLTLDR_MAIL_SENDER')
    MAIL_PASSWORD = os.environ.get('TOOLTLDR_MAIL_PASSWORD')
    MAIL_SERVER = os.environ.get("TOOLTLDR_MAIL_SERVER")
    MAIL_PORT = os.environ.get("TOOLTLDR_MAIL_PORT")
    MAIL_USE_TLS = True
    MAIL_SUBJECT_PREFIX = '[Tool TL;DR]'

    # Flask Admin
    ADMIN = os.environ.get('TOOL_TLDR_ADMIN')

    # Flask-Cache
    CACHE_TYPE = "filesystem"
    CACHE_DIR = "/tmp/website_cache"
    CACHE_DEFAULT_TIMEOUT = 50

    # Pagination Limits
    POPULAR_PAGE_COUNT = 16
    EDITS_PER_PAGE = 20
    USER_EDITS_SHOWN = 11
    ALTS_PER_LIST = 10

    # Promotion Edit Thresholds
    REGISTERED_TO_CONFIRMED_EDITS = 20
    CONFIRMED_TO_TIME_TRAVELER_EDITS = 100

    # Promotion Time Thresholds
    REGISTERED_TO_CONFIRMED_DAYS = 14
    CONFIRMED_TO_TIME_TRAVELER_DAYS = 42

    # Are we blocking users?
    BLOCKING_USERS = True

    # Flask-Talisman
    CSP = {}

    # Flask Debug Toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

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
