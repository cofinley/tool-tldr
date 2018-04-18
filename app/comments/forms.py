from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import Length, DataRequired


class CommentForm(FlaskForm):
    body = TextAreaField("Comment", validators=[DataRequired(), Length(1, 500)])
    parent_comment_id = HiddenField()
    submit = SubmitField("Submit")
