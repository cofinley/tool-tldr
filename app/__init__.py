from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from werkzeug.contrib.cache import RedisCache
from flask_cache import Cache
from flask_mail import Mail
from flask_login import LoginManager
from config import config
import flask_whooshalchemyplus
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SignallingSession
from .history_meta import versioned_session


bootstrap = Bootstrap()
mail = Mail()
versioned_session(SignallingSession)
db = SQLAlchemy()
cache = Cache()

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"


def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	bootstrap.init_app(app)
	mail.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)

	cache_config = {
		"CACHE_TYPE": app.config["CACHE_TYPE"],
		"CACHE_REDIS_URL": app.config["CACHE_REDIS_URL"]
	}
	cache.init_app(app, config=cache_config)

	flask_whooshalchemyplus.init_app(app)
	app.jinja_env.add_extension('jinja2.ext.loopcontrols')

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix="/auth")

	return app
