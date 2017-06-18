from migrate.versioning import api
from flask import current_app
# from config import SQLALCHEMY_DATABASE_URI
# from config import SQLALCHEMY_MIGRATE_REPO

SQLALCHEMY_DATABASE_URI = current_app.config.get("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_MIGRATE_REPO = current_app.config.get("SQLALCHEMY_MIGRATE_REPO")
api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print('Current database version: ' + str(v))