from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, ValidationError, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Regexp
from ..models import Camera, User
from flask_login import current_user

class AddCameraForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(1, 64)])
    phone_number = StringField(validators=[DataRequired(), Length(1, 10)])
    security = BooleanField()
    ip = StringField(validators=[Regexp(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')])
    place = SelectField(default='Home', choices=[('Home', 'Home'), ('Building', 'Building'), 
                                                ('Square', 'Square'), ('Sreet', 'Street'), 
                                                ('Personalized', 'Personalized'),])

    address = StringField(validators=[DataRequired()])
    alerts = SelectMultipleField(choices=[(1, "Fires"),  (2, "Bladed Weapon"), 
                                  (4, "Stabbing"), (8, "Handgun"),
                                  (16, "Long Gun"), (32, "Brandishing"),
                                  (64, "Dog Aggression"), (128, "Car Accident"), 
                                  (256, "Brawls"), (512, "Injured People")])
    
    # validate methods
    def validate_name(self, field):
        if User.objects(user=current_user, name=field.data).first():
            raise ValidationError('You have already registered a camera with this name.')
        
    def validate_ip(self, field):
        if Camera.objects(ip=field.data).first():
            raise ValidationError("A camera already exists with this IP address.")
    
