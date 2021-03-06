from flask import request, redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_administrator

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class UserModelView(MyModelView):
    edit_modal = True
    can_delete = False
    column_exclude_list = ["password_hash", "edits", "comments"]
    column_export_exclude_list = ["password_hash"]
    form_excluded_columns = ["password_hash",
                             "tool_edits",
                             "category_edits",
                             "edits",
                             "user_since",
                             "last_seen",
                             "comments"]
    column_searchable_list = ["username", "email"]


class PageModelView(MyModelView):
    edit_modal = True
    can_delete = False
    form_excluded_columns = ["tools",
                             "edit_time",
                             "children",
                             "versions",
                             "is_time_travel_edit",
                             "author",
                             "comments"]
    column_searchable_list = ["name"]
