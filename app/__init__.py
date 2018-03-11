from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache
from flask_mail import Mail
from flask_login import LoginManager
from config import config
import flask_whooshalchemyplus
from sqlalchemy_continuum import make_versioned
from flask_admin import Admin
from flask_sslify import SSLify
from flask_talisman import Talisman

from .admin.model_views import UserModelView, PageModelView
from .admin.views import FlaskAdminIndexView

from extra_packages.flask_bootstrap4 import Bootstrap

admin = Admin(index_view=FlaskAdminIndexView(), template_mode="bootstrap3")
bootstrap = Bootstrap()
mail = Mail()
make_versioned()
db = SQLAlchemy()
cache = Cache()

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"


def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	admin.init_app(app)
	bootstrap.init_app(app)
	mail.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	SSLify(app)

	csp = app.config["CSP"]

	Talisman(app,
			 content_security_policy=csp,
			 content_security_policy_nonce_in=['script-src'])

	cache_config = {
		"CACHE_TYPE": app.config["CACHE_TYPE"],
		"CACHE_DIR": app.config["CACHE_DIR"],
		"CACHE_DEFAULT_TIMEOUT": app.config["CACHE_DEFAULT_TIMEOUT"]
	}
	cache.init_app(app, config=cache_config)

	flask_whooshalchemyplus.init_app(app)
	app.jinja_env.add_extension('jinja2.ext.loopcontrols')

	from .models import User, Category, Tool

	admin.add_view(UserModelView(User, db.session))
	admin.add_view(PageModelView(Category, db.session))
	admin.add_view(PageModelView(Tool, db.session))

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix="/auth")

	return app
