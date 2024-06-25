from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, ValidationError, SelectField, RadioField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp
from flask_login import current_user


class ReportProblemEmailForm(FlaskForm):
    general_description = StringField(validators=[Length(1,80)])
    description = TextAreaField(validators=[Length(1,200)])
    