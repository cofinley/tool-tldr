from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
	SubmitField, HiddenField
from wtforms.validators import DataRequired, InputRequired, Length, Email, Regexp, URL
from wtforms import ValidationError
from ..models import Role, User, Permission
from ..utils import is_at_or_below_category
from typing import List


class RequiredIf(DataRequired):
	# a validator which makes a field required if
	# another field is set and has a truthy value

	def __init__(self, other_fields: List[str], *args, **kwargs):
		self.other_fields = other_fields
		super(RequiredIf, self).__init__(*args, **kwargs)

	def __call__(self, form, field):
		fields = []
		for _field in self.other_fields:
			fields.append(form._fields.get(_field))
		if not fields:
			raise Exception("no field named '%s' in form" % ", ".join(self.other_fields))
		if any(field.data for field in fields):
			super(RequiredIf, self).__call__(form, field)


class EditProfileForm(FlaskForm):
	name = StringField('Your name', validators=[Length(0, 64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1, 64),
											 Email()])
	username = StringField('Username', validators=[
		DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
										  'Usernames must have only letters, '
										  'numbers, dots or underscores')])
	confirmed = BooleanField('Confirmed')
	role = SelectField('Role', coerce=int)
	name = StringField('Real name', validators=[Length(0, 64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name)
							 for role in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self, field):
		if field.data != self.user.email and \
				User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

	def validate_username(self, field):
		if field.data != self.user.username and \
				User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use.')


class EditCategoryPageForm(FlaskForm):

	name = StringField("Name", validators=[DataRequired(), Length(1, 64)])
	move_parent = BooleanField("Move page?")
	parent_category = StringField("Parent Category", validators=[RequiredIf(["move_parent"]), Length(max=64)])
	parent_category_id = HiddenField()
	what = TextAreaField("What", validators=[DataRequired(), Length(1, 200)])
	why = TextAreaField("Why", validators=[DataRequired(), Length(1, 200)])
	where = TextAreaField("Where", validators=[DataRequired(), Length(1, 200)])
	edit_msg = StringField("Edit Message", validators=[DataRequired(), Length(1, 100)])
	submit = SubmitField('Submit')

	def __init__(self, current_category_id, *args, **kwargs):
		super(EditCategoryPageForm, self).__init__(*args, **kwargs)
		self.current_category_id = current_category_id

	def validate(self):
		if not super().validate():
			return False
		if self.move_parent.data:
			if is_at_or_below_category(self.parent_category_id.data, self.current_category_id):
				self.parent_category_id.errors.append("The current category's parent cannot not be a subcategory or itself.")
				return False
		return True


class EditToolPageForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired(), Length(1, 64)])

	move_parent = BooleanField("Move page?")
	parent_category = StringField("Parent Category", validators=[RequiredIf(["move_parent"]), Length(max=64)])
	parent_category_id = HiddenField()

	edit_avatar_url = BooleanField("Change avatar URL?")
	avatar_url = StringField("Avatar URL", validators=[RequiredIf(["edit_avatar_url"]), URL(), Length(1, 200)])

	env = StringField("Environment", validators=[DataRequired(), Length(1, 64)])
	created = StringField("Date Created", validators=[DataRequired(), Length(1, 25)])
	project_version = StringField("Project Version", validators=[DataRequired(), Length(1, 10)])
	is_active = SelectField("Active?", choices=[(True, "Yes"), (False, "No")], validators=[InputRequired()],
							coerce=lambda x: x == "True")

	edit_link = BooleanField("Change project URL?")
	link = StringField("Project URL", validators=[DataRequired(), URL(), Length(1, 200)])

	why = TextAreaField("Why", validators=[DataRequired(), Length(1, 200)])
	edit_msg = StringField("Edit Message", validators=[DataRequired(), Length(1, 100)])
	recaptcha = RecaptchaField(validators=[RequiredIf(["edit_avatar_url", "edit_link"])])
	submit = SubmitField('Submit')


class TimeTravelForm(FlaskForm):
	edit_msg = StringField("Edit Message", validators=[DataRequired(), Length(1, 100)])
	submit = SubmitField('Submit')


class AddNewToolForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired(), Length(1, 64)])
	parent_category = StringField("Parent Category", validators=[DataRequired(), Length(max=64)])
	parent_category_id = HiddenField()
	avatar_url = StringField("Avatar URL", validators=[DataRequired(), URL(), Length(1, 200)])
	env = StringField("Environment", validators=[DataRequired(), Length(1, 64)])
	created = StringField("Date Created", validators=[DataRequired(), Length(1, 25)])
	project_version = StringField("Project Version", validators=[DataRequired(), Length(1, 10)])
	is_active = SelectField("Active?", choices=[(True, "Yes"), (False, "No")], validators=[InputRequired()],
							coerce=lambda x: x == "True", default="True")
	link = StringField("Project URL", validators=[DataRequired(), URL(), Length(1, 200)])
	why = TextAreaField("Why", validators=[DataRequired(), Length(1, 200)])
	recaptcha = RecaptchaField()
	submit = SubmitField('Submit')


class AddNewCategoryForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired(), Length(1, 64)])
	parent_category = StringField("Parent Category", validators=[Length(max=64)])
	parent_category_id = HiddenField()
	what = TextAreaField("What", validators=[DataRequired(), Length(1, 200)])
	why = TextAreaField("Why", validators=[DataRequired(), Length(1, 200)])
	where = TextAreaField("Where", validators=[DataRequired(), Length(1, 200)])
	submit = SubmitField('Submit')

