"""Formulario para reportar un problema."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import Length


class ReportProblemEmailForm(FlaskForm):
    """Problema que el usuario reporta al equipo de soporte."""

    general_description = StringField(validators=[Length(1, 80)])
    description = TextAreaField(validators=[Length(1, 200)])
