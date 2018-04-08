from flask import abort
from flask_admin import AdminIndexView, expose
from flask_login import current_user, login_required


class FlaskAdminIndexView(AdminIndexView):
    @login_required
    @expose('/')
    @expose('/<path:path>')
    def index(self):
        if not current_user.is_administrator:
            abort(403)
        return super(FlaskAdminIndexView, self).index()
