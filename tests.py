import unittest
from app import db, models, utils
import datetime


class TestCase(unittest.TestCase):
	def test_link(self):
		t1 = models.Tool(id=1,
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
		t2 = models.Tool(id=2,
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

	def test_bottom_up_tree(self):
		parent_id = 18
		parent_list = utils.build_bottom_up_tree(parent_id)
		for i, parent in enumerate(parent_list):
			print((" " * 2 * i), parent.name)


def tear_down_tools():
	tools = models.Tool.query.all()
	for tool in tools:
		db.session.delete(tool)
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
		revision_owner=1,
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
		revision_owner=1,
		env="ruby",
		name_lower="ruby on rails"
	)

	db.session.add(t1)
	db.session.add(t2)
	db.session.add(t3)
	db.session.commit()
