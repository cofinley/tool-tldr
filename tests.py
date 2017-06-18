import unittest
from app import db, models, utils
import datetime


class AltTestCase(unittest.TestCase):
	def test_link(self):
		t1 = models.Tool(
			id=1,
			name="Flask",
			avatar_url="https://google.com",
			parent_category_id=18,
			env="Python",
			created="April 12, 2010",
			version="0.12",
			link="https://flask.pocoo.com",
			what="lipsum",
			why="lipsum",
			where="lipsum",
			revision_number=0,
			revision_owner=1
		)
		t2 = models.Tool(
			id=2,
			name="Flask2",
			avatar_url="https://google2.com",
			parent_category_id=18,
			env="Python",
			created="April 13, 2010",
			version="0.12",
			link="https://flask.pocoo.com",
			what="lipsum2",
			why="lipsu2m",
			where="lipsum2",
			revision_number=0,
			revision_owner=1
		)

		db.session.add(t1)
		db.session.add(t2)
		db.session.commit()
		assert t1.remove_alt(t2) is None
		t = t1.add_alt(t2)
		db.session.add(t)
		db.session.commit()
		assert t1.add_alt(t2) is None
		assert t1.has_alt(t2)
		assert t1.dest_alts.count() == 1
		assert t1.dest_alts.first().name == "Flask2"
		assert t2.src_alts.count() == 1
		assert t2.src_alts.first().name == "Flask"
		t = t1.remove_alt(t2)
		assert t is not None
		db.session.add(t)
		db.session.commit()
		assert not t1.has_alt(t2)
		assert t1.dest_alts.count() == 0
		assert t2.src_alts.count() == 0


class PasswordHashTestCase(unittest.TestCase):
	def test_password_setter(self):
		u = models.User(
			username="test",
			email="test@test.com",
			password='cat'
		)
		self.assertTrue(u.password_hash is not None)

	def test_no_password_getter(self):
		u = models.User(
			username="test",
			email="test@test.com",
			password='cat'
		)
		with self.assertRaises(AttributeError):
			u.password

	def test_password_verification(self):
		u = models.User(
			username="test",
			email="test@test.com",
			password='cat'
		)
		self.assertTrue(u.verify_password('cat'))
		self.assertFalse(u.verify_password('dog'))

	def test_password_salts_are_random(self):
		u = models.User(
			username="test",
			email="test@test.com",
			password='cat'
		)
		u2 = models.User(
			username="test",
			email="test@test.com",
			password='cat'
		)
		self.assertTrue(u.password_hash != u2.password_hash)


def tear_down_roles():
	r = models.Role.query.all()
	for role in r:
		db.session.delete(role)
	db.session.commit()


def tear_down_users():
	u = models.User.query.all()
	for user in u:
		db.session.delete(user)
	db.session.commit()


def tear_down_tools():
	tools = models.Tool.query.all()
	for tool in tools:
		db.session.delete(tool)
	db.session.commit()


def create_mock_roles():
	admin = models.Role(name="Admin")
	mod = models.Role(name="Moderator")
	user = models.Role(name="User")
	db.session.add(admin)
	db.session.add(mod)
	db.session.add(user)
	db.session.commit()


def create_mock_users():
	admin_user = models.User(username="Test Admin", email="admins@testing.com", password="test", role_id=1)
	mod_user = models.User(username="Test Mod", email="mod@testing.com", password="test", role_id=2)
	user_user = models.User(username="Test User", email="user@testing.com", password="test", role_id=3)
	db.session.add(admin_user)
	db.session.add(mod_user)
	db.session.add(user_user)
	db.session.commit()


def create_mock_tools():
	t1 = models.Tool(
		name="Flask",
		avatar_url="http://flask.pocoo.org/docs/0.12/_static/flask.png",
		parent_category_id=18,
		created="April 12, 2010",
		version="0.12",
		link="http://flask.pocoo.org",
		what="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean tempor massa id tellus tempor, eget aliquam sapien vehicula. Praesent a tortor aliquet, pulvinar elit eget, hendrerit erat.",
		where="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean tempor massa id tellus tempor, eget aliquam sapien vehicula. Praesent a tortor aliquet, pulvinar elit eget, hendrerit erat.",
		why="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean tempor massa id tellus tempor, eget aliquam sapien vehicula. Praesent a tortor aliquet, pulvinar elit eget, hendrerit erat.",
		revision_number=0,
		revision_created_time=datetime.datetime.utcnow(),
		revision_modified_time=datetime.datetime.utcnow(),
		revision_owner=1,
		env="python",
		name_lower="flask"
	)

	t2 = models.Tool(
		name="Django",
		avatar_url="https://www.djangoproject.com/s/img/logos/django-logo-positive.png",
		parent_category_id=18,
		created="April 13, 2010",
		version="1.11.2",
		link="https://www.djangoproject.com/",
		what="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean tempor massa id tellus tempor, eget aliquam sapien vehicula. Praesent a tortor aliquet, pulvinar elit eget, hendrerit erat.",
		where="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean tempor massa id tellus tempor, eget aliquam sapien vehicula. Praesent a tortor aliquet, pulvinar elit eget, hendrerit erat.",
		why="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean tempor massa id tellus tempor, eget aliquam sapien vehicula. Praesent a tortor aliquet, pulvinar elit eget, hendrerit erat.",
		revision_number=0,
		revision_created_time=datetime.datetime.utcnow(),
		revision_modified_time=datetime.datetime.utcnow(),
		revision_owner=2,
		env="python",
		name_lower="django"
	)

	t3 = models.Tool(
		name="Ruby on Rails",
		avatar_url="http://rubyonrails.org/images/rails-logo.svg",
		parent_category_id=18,
		created="April 14, 2010",
		version="5.1.1",
		link="http://rubyonrails.org/",
		what="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean tempor massa id tellus tempor, eget aliquam sapien vehicula. Praesent a tortor aliquet, pulvinar elit eget, hendrerit erat.",
		where="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean tempor massa id tellus tempor, eget aliquam sapien vehicula. Praesent a tortor aliquet, pulvinar elit eget, hendrerit erat.",
		why="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean tempor massa id tellus tempor, eget aliquam sapien vehicula. Praesent a tortor aliquet, pulvinar elit eget, hendrerit erat.",
		revision_number=0,
		revision_created_time=datetime.datetime.utcnow(),
		revision_modified_time=datetime.datetime.utcnow(),
		revision_owner=3,
		env="ruby",
		name_lower="ruby on rails"
	)

	db.session.add(t1)
	db.session.add(t2)
	db.session.add(t3)
	db.session.commit()


def reset_db():
	tear_down_roles()
	tear_down_users()
	tear_down_tools()
	create_mock_roles()
	create_mock_users()
	create_mock_tools()


def test_bottom_up_tree():
	parent_id = 18
	parent_list = utils.build_bottom_up_tree(parent_id)
	for i, parent in enumerate(parent_list):
		print((" " * 2 * i), parent.name)