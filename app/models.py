from . import db, login_manager
from flask import current_app
from whoosh.analysis import FancyAnalyzer
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Permission:
	WRITE_ARTICLES = 0x04
	MODERATE_COMMENTS = 0x08
	ADMINISTER = 0x80


class Role(db.Model):
	__tablename__ = "roles"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship("User", backref="role", lazy="dynamic")

	def __repr__(self):
		return "<Role %r>" % self.name


class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	tools = db.relationship("Tool", backref="author", lazy="dynamic")
	role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
	confirmed = db.Column(db.Boolean, default=False)

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
		return self.role is not None and \
			   (self.role.permissions & permissions) == permissions

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

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


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class Category(db.Model):
	__tablename__ = "categories"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
	parent = db.relationship('Category', remote_side=[id], backref='children')
	tools = db.relationship("Tool", backref="category", lazy="dynamic")

	def __repr__(self):
		return "<Category %d: %r>" % (self.id, self.name)


# Define many-to-many association table
# Tools will have many alternatives and those alternatives will also have many alternatives
# src == source == this tool's id was seen in another (source) tool's alts
# dest == destination == this tool is linking to other (destination) tools as its alts
src_alts = db.Table("src_alts",
					   db.Column("src", db.Integer, db.ForeignKey("tools.id")),
					   db.Column("dest", db.Integer, db.ForeignKey("tools.id"))
)


class Tool(db.Model):
	__tablename__= "tools"
	__searchable__ = ["name"]
	__analyzer__ = FancyAnalyzer()

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	name_lower = db.Column(db.String(50))
	avatar_url = db.Column(db.String(150))
	parent_category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
	env = db.Column(db.String(30))
	created = db.Column(db.String(25))
	version = db.Column(db.String(10))
	link = db.Column(db.String(150))
	what = db.Column(db.String(200))
	why = db.Column(db.String(200))
	where = db.Column(db.String(200))
	dest_alts = db.relationship("Tool",
								secondary=src_alts,
								primaryjoin=src_alts.c.src == id,
								secondaryjoin=src_alts.c.dest == id,
								backref=db.backref("src_alts", lazy="dynamic"),
								lazy="dynamic")
	revision_number = db.Column(db.Integer)
	revision_created_time = db.Column(db.DateTime)
	revision_modified_time = db.Column(db.DateTime)
	revision_owner = db.Column(db.Integer, db.ForeignKey("users.id"))

	def add_alt(self, tool):
		if not self.has_alt(tool):
			self.dest_alts.append(tool)
			return self

	def remove_alt(self, tool):
		if self.has_alt(tool):
			self.dest_alts.remove(tool)
			return self

	def has_alt(self, tool):
		return self.dest_alts.filter(src_alts.c.dest == tool.id).count() > 0

	def __repr__(self):
		return "<Tool %d: %r>" % (self.id, self.name)


# flask_whooshalchemyplus.init_app(app)