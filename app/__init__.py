from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask.ext.cache import Cache
from config import config

app = Flask(__name__)
app.config.from_object(config["default"])
# app.config.from_object('config')
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
db = SQLAlchemy(app)
# cache = Cache(app, config={"CACHE_TYPE": "redis"})

from app import views, models