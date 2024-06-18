from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, ValidationError, SelectField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp
from ..models import Camera, User
from flask_login import current_user


class BaseCameraForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(1, 30)])
    phone_number = StringField(validators=[DataRequired(), Regexp('^\d{10}$', 0, 'Phone numbers must be exactly 10 digits and contain only numbers.')])
    camera_type = RadioField('Camera Type', choices=[('WebCamera', 'Web Camera'), ('SecurityCamera', 'Security Camera')], validators=[DataRequired()])
    url = StringField()
    place = SelectField(default='Personalized', choices=[('Home', 'Home'), ('Building', 'Building'), 
                                                ('Square', 'Square'), ('Street', 'Street'), 
                                                ('Personalized', 'Personalized'),])
    address = StringField(validators=[DataRequired()])
    device_id = SelectField('Device ID', choices=[], coerce=str)
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

    # validate methods
    def validate_name(self, field):
        existing_camera = Camera.objects(user=current_user.id, name=field.data).first()
        if existing_camera:
            raise ValidationError('You have already registered a camera with this name.')
             
    def validate_ip(self, field):
        if Camera.objects(ip=field.data).first() and self.camera_type.data == "SecurityCamera":
            raise ValidationError("A camera already exists with this IP address.")
        
class EditCameraForm(BaseCameraForm):
    place = SelectField(default='Personalized', choices=[('Home', 'Home'), ('Building', 'Building'), 
                                                ('Square', 'Square'), ('Street', 'Street'), 
                                                ('Personalized', 'Personalized'), 
                                                ('Default', 'Default'),])
        
        
class ReportNotification(FlaskForm):
    title = StringField(validators=[DataRequired(), Length(1, 64)])
    description = TextAreaField(validators=[DataRequired(), Length(1, 312)])
