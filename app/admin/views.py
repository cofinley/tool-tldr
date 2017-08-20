from flask import redirect, request, url_for
from flask_login import current_user
from flask_admin import AdminIndexView, expose


class FlaskAdminIndexView(AdminIndexView):
	@expose('/')
	@expose('/<path:path>')
	def index(self):
		if not current_user.is_administrator:
			return redirect(url_for('auth.login', next=request.url))
		return super(FlaskAdminIndexView, self).index()