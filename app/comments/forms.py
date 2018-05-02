from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import Length, DataRequired, ValidationError

from .. import db, models


class CommentForm(FlaskForm):
    body = TextAreaField("Comment", validators=[DataRequired(), Length(1, 500)])
    parent_comment_id = HiddenField()
    submit = SubmitField("Submit")

    def validate_parent_comment_id(self, field):
        if field.data != "":
            if not db.session.query(models.Comment.id).filter_by(id=int(field.data)).scalar():
                raise ValidationError("Invalid parent comment.")
