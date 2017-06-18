from app import db, app
import flask_whooshalchemyplus
from whoosh.analysis import FancyAnalyzer
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	tools = db.relationship("Tool", backref="author", lazy="dynamic")

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

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


class Category(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	parent = db.relationship('Category', remote_side=[id], backref='children')
	tools = db.relationship("Tool", backref="category", lazy="dynamic")

	def __repr__(self):
		return "<Category %d : %r>" % (self.id, self.name)


# Define many-to-many association table
# Tools will have many alternatives and those alternatives will also have many alternatives
# src == source == this tool's id was seen in another (source) tool's alts
# dest == destination == this tool is linking to other (destination) tools as its alts
src_alts = db.Table("src_alts",
					   db.Column("src", db.Integer, db.ForeignKey("tool.id")),
					   db.Column("dest", db.Integer, db.ForeignKey("tool.id"))
)


class Tool(db.Model):
	__tablename__= "tool"
	__searchable__ = ["name"]
	__analyzer__ = FancyAnalyzer()

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	name_lower = db.Column(db.String(50))
	avatar_url = db.Column(db.String(150))
	parent_category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
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
	revision_owner = db.Column(db.Integer, db.ForeignKey("user.id"))

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


flask_whooshalchemyplus.init_app(app)