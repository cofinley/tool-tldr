from datetime import datetime

import sqlalchemy as sa
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from flask_sqlalchemy import BaseQuery
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from slugify import slugify
from sqlalchemy.orm import deferred, backref
from werkzeug.security import generate_password_hash, check_password_hash
from whoosh.analysis import FancyAnalyzer

from . import db, login_manager, utils


class QueryWithSoftDelete(BaseQuery):
    _with_deleted = False

    def __new__(cls, *args, **kwargs):
        obj = super(QueryWithSoftDelete, cls).__new__(cls)
        obj._with_deleted = kwargs.pop('_with_deleted', False)
        if len(args) > 0:
            super(QueryWithSoftDelete, obj).__init__(*args, **kwargs)
            return obj.filter_by(deleted=None) if not obj._with_deleted else obj
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(db.class_mapper(self._mapper_zero().class_),
                              session=db.session(), _with_deleted=True)

    def _get(self, *args, **kwargs):
        # this calls the original query.get function from the base class
        return super(QueryWithSoftDelete, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        # the query.get method does not like it if there is a filter clause
        # pre-loaded, so we need to implement it using a workaround
        obj = self.with_deleted()._get(*args, **kwargs)
        return obj if obj is None or self._with_deleted or not obj.deleted else None


envs = db.Table(
    "tool_environments",
    db.Column("tool_id", db.Integer, db.ForeignKey("tools.id"), primary_key=True),
    db.Column("environment_id", db.Integer, db.ForeignKey("environments.id"), primary_key=True)
)


class Environment(db.Model):
    __tablename__ = "environments"
    __searchable__ = ["name"]
    __analyzer__ = FancyAnalyzer()
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    @property
    def html(self):
        return "<span class='tool-environment'>{}</span>".format(utils.escape_html(self.name))

    def __repr__(self):
        return "<Env %d: %r" % (self.id, self.name)


class Tool(db.Model):
    __tablename__ = "tools"
    __searchable__ = ["name"]
    __analyzer__ = FancyAnalyzer()
    __versioned__ = {}
    query_class = QueryWithSoftDelete

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    deleted = db.Column(db.DateTime())
    environments_dumped = db.Column(db.String(75))
    # Relationships
    parent_category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    comments = db.relationship("Comment", backref="parent_tool_page", lazy="dynamic")
    environments = db.relationship("Environment", secondary=envs,
                                   backref=db.backref('tools', lazy="dynamic"))
    # Page-specific Columns
    logo_url = deferred(db.Column(db.String(200)), group="page")
    is_active = deferred(db.Column(db.Boolean, default=True), group="page")
    created = deferred(db.Column(db.Integer()), group="page")
    project_version = deferred(db.Column(db.String(10)), group="page")
    link = deferred(db.Column(db.String(200)), group="page")
    what = deferred(db.Column(db.String(250)), group="page")
    why = deferred(db.Column(db.String(250)), group="page")
    # Edit-specific columns
    edit_msg = deferred(db.Column(db.String(100), default="Initial edit"), group="edits")
    edit_time = deferred(db.Column(db.DateTime(), default=datetime.utcnow), group="edits")
    edit_author = deferred(db.Column(db.Integer, db.ForeignKey("users.id")), group="edits")
    is_time_travel_edit = deferred(db.Column(db.Boolean, default=False), group="edits")

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def environments_html(self):
        return "<div class='tool-environments'>" + "".join([env.html for env in self.environments]) + "</div>"

    def __repr__(self):
        return "<Tool %d: %r>" % (self.id, self.name)


class Category(db.Model):
    __tablename__ = "categories"
    __searchable__ = ["name"]
    __analyzer__ = FancyAnalyzer()
    __versioned__ = {}
    query_class = QueryWithSoftDelete

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    what = db.Column(db.String(250))
    deleted = db.Column(db.DateTime())
    # Relationships
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    parent = db.relationship('Category', remote_side=[id], backref=backref('children', lazy="dynamic"))
    tools = db.relationship("Tool", backref="category", lazy="dynamic")
    comments = db.relationship("Comment", backref="parent_category_page", lazy="dynamic")
    # Page-specific Columns
    why = deferred(db.Column(db.String(250)), group="page")
    where = deferred(db.Column(db.String(250)), group="page")
    # Page-specific Columns
    edit_msg = deferred(db.Column(db.String(100), default="Initial edit"), group="edits")
    edit_time = deferred(db.Column(db.DateTime(), default=datetime.utcnow), group="edits")
    edit_author = deferred(db.Column(db.Integer, db.ForeignKey("users.id")), group="edits")
    is_time_travel_edit = deferred(db.Column(db.Boolean, default=False), group="edits")

    @property
    def slug(self):
        return slugify(self.name)

    def __repr__(self):
        return "<Category %d: %r>" % (self.id, self.name)


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    edit_time = db.Column(db.DateTime())
    deleted = db.Column(db.DateTime())
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    parent_comment = db.relationship('Comment', remote_side=[id], backref='replies')
    parent_category_page_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    parent_tool_page_id = db.Column(db.Integer, db.ForeignKey("tools.id"))

    def __repr__(self):
        return "<Comment %d>" % self.id


class User(db.Model, UserMixin):
    __tablename__ = "users"
    query_class = QueryWithSoftDelete

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = deferred(db.Column(db.String(120), index=True, unique=True))
    password_hash = deferred(db.Column(db.String(128)))
    confirmed = db.Column(db.Boolean, default=False)
    blocked = db.Column(db.DateTime())
    deleted = db.Column(db.DateTime())
    # Relationships
    tool_edits = db.relationship('Tool', backref="author", lazy="dynamic")
    role_id = deferred(db.Column(db.Integer, db.ForeignKey("roles.id")), group="profile")
    category_edits = db.relationship('Category', backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author")
    # Profile-specific columns
    name = deferred(db.Column(db.String(64)), group="profile")
    about_me = deferred(db.Column(db.Text(500)), group="profile")
    user_since = deferred(db.Column(db.DateTime(), default=datetime.utcnow), group="profile")
    last_seen = deferred(db.Column(db.DateTime(), default=datetime.utcnow), group="profile")
    edits = deferred(db.Column(db.Integer, default=0), group="profile")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def can(self, permissions):
        # permissions is (usually) the lower value
        # If the user's role's permissions outweigh it, the function will return the lesser permission
        # If the user does not have the permission, it will return 0
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    @property
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def is_time_traveler(self):
        return self.can(Permission.TIME_TRAVEL)

    @property
    def is_member(self):
        # confirmed users don't need captcha to change links
        # 0x0f == 15 == shortcut for all permissions included in confirmed user
        return self.can(0x0f)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return "<User %r>" % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    @property
    def is_administrator(self):
        return False

    @property
    def is_authenticated(self):
        return False

    @property
    def is_member(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    CHANGE_LINKS = 0x01
    CREATE = 0x02
    UPLOAD = 0x04
    MOVE = 0x08
    TIME_TRAVEL = 0x10
    DELETE = 0x20
    LOCK = 0x40
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship("User", backref="role", lazy="dynamic")
    permissions = db.Column(db.Integer)

    @staticmethod
    def insert_roles():
        roles = {
            "Anonymous User": (Permission.CHANGE_LINKS, True),
            "User": (Permission.CREATE | Permission.CHANGE_LINKS, True),
            "Member": (Permission.CREATE |
                          Permission.CHANGE_LINKS |
                          Permission.UPLOAD |
                          Permission.MOVE, False),
            "Time Traveler": (Permission.CREATE |
                              Permission.CHANGE_LINKS |
                              Permission.UPLOAD |
                              Permission.MOVE |
                              Permission.TIME_TRAVEL, False),
            "Administrator": (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role %r>" % self.name


# Configure mappers for SQLAlchemy-Continuum
sa.orm.configure_mappers()
