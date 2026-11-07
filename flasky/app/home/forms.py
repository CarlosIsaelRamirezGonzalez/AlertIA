"""Formularios de cámaras y de reportes."""

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (BooleanField, HiddenField, RadioField, SelectField, StringField, TextAreaField,
                     ValidationError)
from wtforms.validators import DataRequired, Length, Regexp

from ..models import Camera

PHONE_PATTERN = r'^\d{10}$'
PHONE_MESSAGE = 'Phone numbers must be exactly 10 digits and contain only numbers.'
PLACE_CHOICES = [('Home', 'Home'), ('Building', 'Building'), ('Square', 'Square'),
                 ('Street', 'Street'), ('Personalized', 'Personalized')]


class BaseCameraForm(FlaskForm):
    """Datos de una cámara nueva, con una casilla por alerta."""

    name = StringField(validators=[Length(1, 30)])
    phone_number = StringField(validators=[Regexp(PHONE_PATTERN, 0, PHONE_MESSAGE)])
    camera_type = RadioField('Camera Type', choices=[('WebCamera', 'Web Camera'), ('SecurityCamera', 'Security Camera')])
    url = StringField()
    place = SelectField(default='Personalized', choices=PLACE_CHOICES)
    latitude = HiddenField()
    longitude = HiddenField()
    address = StringField(validators=[DataRequired()])
    device_id = SelectField('Device ID', choices=[], coerce=str)

    # Alertas: los nombres coinciden con models.Alerts.
    fires = BooleanField()
    bladed_weapon = BooleanField()
    stabbing = BooleanField()
    handgun = BooleanField()
    long_gun = BooleanField()
    cannoning = BooleanField()
    dog_attack = BooleanField()
    car_accident = BooleanField()
    brawls = BooleanField()
    injured_people = BooleanField()


class AddCameraForm(BaseCameraForm):
    """Registro de una cámara, sin nombres ni direcciones repetidas."""

    def validate_name(self, field):
        """Rechaza un nombre que el usuario ya usó en otra cámara.

        Args:
            field: Campo del nombre.

        Raises:
            ValidationError: Si el nombre ya existe.
        """
        if Camera.objects(user=current_user.id, name=field.data).first():
            raise ValidationError('You have already registered a camera with this name.')

    def validate_url(self, field):
        """Rechaza una cámara de seguridad con una dirección ya registrada.

        Args:
            field: Campo de la dirección.

        Raises:
            ValidationError: Si la dirección ya existe.
        """
        if field.data and self.camera_type.data == "SecurityCamera" and Camera.objects(url=field.data).first():
            raise ValidationError("A camera already exists with this IP address.")


class EditCameraForm(FlaskForm):
    """Cambios a una cámara; el tipo y el dispositivo no se pueden cambiar."""

    name = StringField(validators=[Length(1, 30)])
    phone_number = StringField(validators=[Regexp(PHONE_PATTERN, 0, PHONE_MESSAGE)])
    place = SelectField(choices=PLACE_CHOICES)
    latitude = HiddenField()
    longitude = HiddenField()
    address = StringField(validators=[DataRequired()])
    fires = BooleanField()
    bladed_weapon = BooleanField()
    stabbing = BooleanField()
    handgun = BooleanField()
    long_gun = BooleanField()
    cannoning = BooleanField()
    dog_attack = BooleanField()
    car_accident = BooleanField()
    brawls = BooleanField()
    injured_people = BooleanField()


class ReportNotification(FlaskForm):
    """Reporte de una notificación que el usuario considera errónea."""

    title = StringField(validators=[DataRequired(), Length(1, 64)])
    description = TextAreaField(validators=[DataRequired(), Length(1, 312)])
