import os
import csv
from datetime import datetime
from app import db, models, create_app


class Helper:
	def __init__(self, config):
		self.config = config
		self.blueprint = create_app(config)
		self.ctx = self.blueprint.test_request_context()
		self.ctx.push()
		self.db = db
		self.models = models

		self.current_dir = os.path.dirname(__file__)

		self.tsv_dir = os.path.join(self.current_dir, "tsv_tables")

	def setup_categories(self):
		categories_table = os.path.join(self.tsv_dir, "categories.tsv")

		with open(categories_table, "r") as tsvin:
			tsvin = csv.reader(tsvin, delimiter="\t")
			next(tsvin, None)

			for row in tsvin:
				id, name, parent_category_id, what, why, where, version = row
				parent_category_id = int(parent_category_id) if (parent_category_id != "") else None
				c = models.Category(
					id=int(id),
					name=name,
					parent_category_id=parent_category_id,
					what=what,
					why=why,
					where=where
				)
				db.session.add(c)
			db.session.commit()

	def setup_tools(self):
		tools_table = os.path.join(self.tsv_dir, "tools.tsv")
		with open(tools_table, "r") as tsvin:
			tsvin = csv.reader(tsvin, delimiter="\t")
			next(tsvin, None)  # skip header

			for row in tsvin:
				id, name, avatar_url, parent_category_id, env, created, project_version, link, why, version = row
				parent_category_id = int(parent_category_id) if (parent_category_id != "") else None
				t = models.Tool(
					id=int(id),
					name=name,
					avatar_url=avatar_url,
					parent_category_id=parent_category_id,
					env=env,
					created=created,
					project_version=project_version,
					link=link,
					why=why
				)
				db.session.add(t)
			db.session.commit()

	def setup_users(self):
		users_table = os.path.join(self.tsv_dir, "users.tsv")
		with open(users_table, "r") as tsvin:
			tsvin = csv.reader(tsvin, delimiter="\t")
			next(tsvin, None)  # skip header

			for row in tsvin:
				id, username, email, password_hash, name, about_me,	member_since, role_name, confirmed, last_seen = row
				u = models.User(
					id=int(id),
					username=username,
					email=email,
					password_hash=password_hash,
					name=name,
					about_me=about_me,
					member_since=datetime.strptime(member_since, "%Y-%m-%d %H:%M:%S.%f"),
					role_id=models.Role.query.filter_by(name=role_name).first().id,
					confirmed=bool(confirmed),
					last_seen=datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S.%f")
				)
				db.session.add(u)
			db.session.commit()

	def setup_all(self):
		db.create_all()
		models.Role.insert_roles()
		self.setup_categories()
		self.setup_tools()
		self.setup_users()

	def reset_all(self):
		db.drop_all()
		self.setup_all()

	@staticmethod
	def drop_all():
		db.drop_all()

	@staticmethod
	def create_all():
		db.create_all()