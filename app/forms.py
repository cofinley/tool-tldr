from flask_wtf import FlaskForm as Form
from wtforms import StringField, BooleanField, PasswordField, validators
from wtforms.validators import DataRequired


class RegistrationForm(Form):
	username = StringField("Username", validators=[DataRequired()])
	email = StringField("Email Address", [validators.Length(min=6, max=35)])
	password = PasswordField("New Password", [
		validators.Length(min=8),
		validators.DataRequired(),
		validators.EqualTo("confirm", message="Passwords must match")
	])
	confirm = PasswordField("Repeat Password")


class LoginForm(Form):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("New Password", [
		validators.Length(min=8),
		validators.DataRequired()])
	remember_me = BooleanField("Remember me", default=False)

