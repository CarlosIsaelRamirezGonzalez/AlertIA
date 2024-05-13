from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, ValidationError, SelectField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp
from ..models import Camera, User
from flask_login import current_user


class AddCameraForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(1, 64)])
    phone_number = StringField(validators=[DataRequired()])
    security = BooleanField()
    ip = StringField()
    place = SelectField(default='Personalized', choices=[('Home', 'Home'), ('Building', 'Building'), 
                                                ('Square', 'Square'), ('Street', 'Street'), 
                                                ('Personalized', 'Personalized'),])
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
    
    
    # validate methods
    def validate_name(self, field):
        existing_camera = Camera.objects(user=current_user.id, name=field.data).first()
        if existing_camera:
            raise ValidationError('You have already registered a camera with this name.')
    
        
        
    def validate_ip(self, field):
        if Camera.objects(ip=field.data).first():
            raise ValidationError("A camera already exists with this IP address.")
        

