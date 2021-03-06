from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, HiddenField, IntegerField, \
    ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, URL, Optional

from .. import db
from ..models import Role, User, Category
from ..utils import is_at_or_below_category

category_what_description = "What is the tl;dr of the category? What do tools in this category let you do?"
category_why_description = "Why would I need to use it? Why would I need to <i>start</i> using it?"
category_where_description = "Where in the application design/pipeline is this category of tools used? <a href='/about#categories-where'>Learn more.</a>"

tool_environment_description = "In what environment(s) is this tool used or found in? Usually, this is a programming lanugage."
tool_what_description = "What is the tl;dr of the tool? How does it differ from the description of its category?"
tool_why_description = "Why use this tool over an alternative?"
tool_active_description = "Is someone still maintaining or actively developing this tool?"

parent_category_description = "Pick a category from the tree."


class RequiredIf(DataRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name: str, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)


class EditProfileForm(FlaskForm):
    name = StringField('Your name (optional)', validators=[Length(0, 64)])
    about_me = TextAreaField('About me (optional)')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')
    ])
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
    what = TextAreaField("What",
                         description=category_what_description,
                         validators=[DataRequired(), Length(1, 250)])
    why = TextAreaField("Why", description=category_why_description,
                        validators=[DataRequired(), Length(1, 250)])
    where = TextAreaField("Where",
                          description=category_where_description,
                          validators=[DataRequired(), Length(1, 250)])
    edit_msg = StringField("Edit Message", validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('Submit')


class EditCategoryPageFormMember(EditCategoryPageForm):
    move_parent = BooleanField("Move page?")
    parent_category = StringField("Parent Category", description=parent_category_description,
                                  validators=[RequiredIf("move_parent"), Length(max=64)])
    parent_category_id = HiddenField()

    def __init__(self, current_category_id, *args, **kwargs):
        super(EditCategoryPageFormMember, self).__init__(*args, **kwargs)
        self.current_category_id = current_category_id

    def validate(self):
        if not super().validate():
            return False
        if self.parent_category_id.data == "":
            self.parent_category.errors.append("Pick a parent category.")
            return False
        if int(self.parent_category_id.data) != 0:
            if not db.session.query(Category.id).filter_by(id=int(self.parent_category_id.data)).scalar():
                self.parent_category.errors.append("Invalid parent category")
                return False
        if self.move_parent.data:
            if is_at_or_below_category(int(self.parent_category_id.data), self.current_category_id):
                self.parent_category.errors.append(
                    "The current category's parent cannot be itself or a subcategory of itself.")
                return False
        return True


class EditToolPageForm(FlaskForm):
    # Required
    name = StringField("Name*", validators=[DataRequired(), Length(1, 64)])
    what = TextAreaField("What*", description=tool_what_description, validators=[DataRequired(), Length(1, 250)])
    why = TextAreaField("Why*", description=tool_why_description, validators=[DataRequired(), Length(1, 250)])
    edit_msg = StringField("Edit Message*", validators=[DataRequired(), Length(1, 100)])

    # Optional
    environments = StringField("Environment(s)", description=tool_environment_description,
                               validators=[Optional()])
    created = IntegerField("Date Created", validators=[Optional()])
    project_version = StringField("Project Version", validators=[Optional(), Length(1, 10)])
    is_active = SelectField("Actively Developed?", description=tool_active_description, validators=[Optional()],
                            choices=[(True, "Yes"), (False, "No")], coerce=lambda x: x == "True")

    logo_url = StringField("Logo URL", validators=[Optional(), URL(), Length(1, 200),
                                                   Regexp("^https://",
                                                              message="Image link must be hosted under https://")])
    link = StringField("Project URL", validators=[Optional(), URL(), Length(1, 200)])

    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')


class EditToolPageFormMember(EditToolPageForm):
    # Remove recaptcha requirement
    recaptcha = None

    move_parent = BooleanField("Move page?")
    parent_category = StringField("Parent Category*", description=parent_category_description,
                                  validators=[RequiredIf("move_parent"), Length(max=64)])
    parent_category_id = HiddenField()

    def validate_parent_category_id(self, field):
        if not db.session.query(Category.id).filter_by(id=int(field.data)).scalar():
            self.parent_category.errors.append("Invalid parent category")
            raise ValidationError("Invalid parent category.")


class TimeTravelForm(FlaskForm):
    edit_msg = StringField("Edit Message", validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('Submit')


class AddNewToolForm(FlaskForm):
    # Required
    name = StringField("Name*", validators=[DataRequired(), Length(1, 64)])
    parent_category = StringField("Parent Category*", description=parent_category_description,
                                  validators=[DataRequired(), Length(max=64)])
    parent_category_id = HiddenField()
    what = TextAreaField("What*", description=tool_what_description, validators=[DataRequired(), Length(1, 250)])
    why = TextAreaField("Why*", description=tool_why_description, validators=[DataRequired(), Length(1, 250)])

    # Optional
    logo_url = StringField("Logo URL", validators=[Optional(), URL(), Length(1, 200),
                                                   Regexp("^https://",
                                                              message="Image link must be hosted under https://")])
    environments = StringField("Environment(s)", description=tool_environment_description,
                               validators=[Optional()])
    created = IntegerField("Date Created", validators=[Optional()])
    project_version = StringField("Project Version", validators=[Optional(), Length(1, 10)])
    is_active = SelectField("Actively Developed?", description=tool_active_description, validators=[Optional()],
                            choices=[(True, "Yes"), (False, "No")], coerce=lambda x: x == "True", default="True")
    link = StringField("Project URL", validators=[Optional(), URL(), Length(1, 200)])

    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')

    def validate_parent_category_id(self, field):
        if not db.session.query(Category.id).filter_by(id=int(field.data)).scalar():
            self.parent_category.errors.append("Invalid parent category")
            raise ValidationError("Invalid parent category.")


class AddNewToolFormMember(AddNewToolForm):
    # Remove recaptcha requirement
    recaptcha = None


class AddNewCategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 64)])
    parent_category = StringField("Parent Category", description=parent_category_description,
                                  validators=[Length(max=64)])
    parent_category_id = HiddenField()
    what = TextAreaField("What", description=category_what_description, validators=[DataRequired(), Length(1, 250)])
    why = TextAreaField("Why", description=category_why_description, validators=[DataRequired(), Length(1, 250)])
    where = TextAreaField("Where", description=category_where_description, validators=[DataRequired(), Length(1, 250)])
    submit = SubmitField('Submit')

    def validate_parent_category_id(self, field):
        if field.data == "":
            self.parent_category.errors.append("Pick a parent category.")
            raise ValidationError("Pick a parent category.")
        if int(field.data) != 0:
            if not db.session.query(Category.id).filter_by(id=int(field.data)).scalar():
                self.parent_category.errors.append("Invalid parent category")
                raise ValidationError("Invalid parent category.")
