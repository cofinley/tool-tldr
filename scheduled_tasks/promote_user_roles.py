import os
from app import db, models, create_app, utils


def promote_roles():
	registered_role_id = models.Role.query.filter_by(name="Registered").first().id
	registered_users = models.User.query.filter_by(role_id=registered_role_id).all()
	promotable_users = [u for u in registered_users
							   if (utils.is_over_x_hours_ago(t=u.member_since, hours=96))
							   and ((u.category_edits.count() + u.tool_edits.count()) >= 1)]

	confirmed_role_id = models.Role.query.filter_by(name="Confirmed").first().id
	for user in promotable_users:
		user.role_id = confirmed_role_id
		db.session.add(user)
		db.session.commit()


if __name__ == "__main__":
	blueprint = create_app(os.getenv('FLASK_CONFIG') or "default")
	ctx = blueprint.test_request_context()
	ctx.push()

	promote_roles()
