import os
from sqlalchemy_continuum import version_class
from app import db, models, create_app, utils

DAYS = 4
EDITS = 10


def promote_roles():
	registered_role_id = models.Role.query.filter_by(name="Registered").first().id
	confirmed_role_id = models.Role.query.filter_by(name="Confirmed").first().id
	registered_users = models.User.query.filter_by(role_id=registered_role_id).all()
	for u in registered_users:
		tool_edits = version_class(models.Tool).query.filter_by(edit_author=u.id).all()
		category_edits = version_class(models.Category).query.filter_by(edit_author=u.id).all()
		total_edits = len(tool_edits) + len(category_edits)

		if utils.is_over_x_hours_ago(t=u.member_since, hours=DAYS*24) and total_edits >= EDITS:
			u.role_id = confirmed_role_id
			db.session.add(u)
			db.session.commit()


if __name__ == "__main__":
	config = os.getenv('FLASK_CONFIG') or "default"
	print("Config:", config)
	blueprint = create_app(config)
	ctx = blueprint.test_request_context()
	ctx.push()

	promote_roles()
