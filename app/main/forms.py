from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
	SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User, Permission
from flask_login import current_user


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
	what = TextAreaField("What", validators=[DataRequired(), Length(1, 200)])
	why = TextAreaField("Why", validators=[DataRequired(), Length(1, 200)])
	where = TextAreaField("Where", validators=[DataRequired(), Length(1, 200)])
	edit_msg = StringField("Edit Message", validators=[DataRequired(), Length(1, 100)])
	submit = SubmitField('Submit')


class EditToolPageForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired(), Length(1, 64)])
	avatar_url = StringField("Avatar URL", validators=[DataRequired(), Length(1, 200)])
	env = StringField("Environment", validators=[DataRequired(), Length(1, 64)])
	created = StringField("Date Created", validators=[DataRequired(), Length(1, 25)])
	project_version = StringField("Project Version", validators=[DataRequired(), Length(1, 10)])
	link = StringField("Project URL", validators=[DataRequired(), Length(1, 200)])
	why = TextAreaField("Why", validators=[DataRequired(), Length(1, 200)])
	edit_msg = StringField("Edit Message", validators=[DataRequired(), Length(1, 100)])
	recaptcha = RecaptchaField()
	submit = SubmitField('Submit')
