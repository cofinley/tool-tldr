import unittest
from app import db, models


class AltTestCase(unittest.TestCase):
	def test_link(self):
		t1 = models.Tool(
			id=1,
			name="Flask",
			avatar_url="https://google.com",
			parent_category_id=18,
			env="Python",
			created="April 12, 2010",
			project_version="0.12",
			link="https://flask.pocoo.com",
			why="lipsum",
		)
		t2 = models.Tool(
			id=2,
			name="Flask2",
			avatar_url="https://google2.com",
			parent_category_id=18,
			env="Python",
			created="April 13, 2010",
			project_version="0.12",
			link="https://flask.pocoo.com",
			why="lipsu2m",
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
