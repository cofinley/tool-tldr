import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('TOOLTLDR_SECRET_KEY')

    # Flask-SQLAlchemy
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 1

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
    USER_TO_MEMBER_EDITS = 20
    MEMBER_TO_TIME_TRAVELER_EDITS = 100

    # Promotion Time Thresholds
    USER_TO_MEMBER_DAYS = 14
    MEMBER_TO_TIME_TRAVELER_DAYS = 42

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
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "https://ajax.googleapis.com",
            "https://cdnjs.cloudflare.com",
            "https://maxcdn.bootstrapcdn.com",
            "https://www.google.com/recaptcha/",
            "https://www.gstatic.com/recaptcha/",
            "https://www.googletagmanager.com",
            "https://www.google-analytics.com"
        ],
        "img-src": "https:",
        "style-src": "'self' https://fonts.googleapis.com 'unsafe-inline'",
        "connect-src": "'self'",
        "font-src": [
            "'self'",
            "https://fonts.gstatic.com"
        ],
        "manifest-src": "'self'",
        "frame-src": "https://www.google.com/recaptcha/"
    }

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        from logging import Formatter

        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_USERNAME,
            toaddrs=[cls.MAIL_USERNAME],
            subject=cls.MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(Formatter('''
        Message type:       %(levelname)s
        Location:           %(pathname)s:%(lineno)d
        Module:             %(module)s
        Function:           %(funcName)s
        Time:               %(asctime)s

        Message:

        %(message)s
        '''))
        app.logger.addHandler(mail_handler)


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
