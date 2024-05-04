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
    alerts = SelectMultipleField(choices=[("Fires", "Fires"),  ("Bladed Weapon", "Bladed Weapon"), 
                                  ("Stabbing", "Stabbing"), ("Handgun", "Handgun"),
                                  ("Long Gun", "Long Gun"), ("Brandishing", "Brandishing"),
                                  ("Dog Aggression", "Dog Aggression"), ("Car Accident", "Car Accident"), 
                                  ("Brawls", "Brawls"), ("Injured People", "Injured People")], default="Fires")
    
    # validate methods
    def validate_name(self, field):
        if User.objects(user=current_user, name=field.data).first():
            raise ValidationError('You have already registered a camera with this name.')
        
    def validate_ip(self, field):
        if Camera.objects(ip=field.data).first():
            raise ValidationError("A camera already exists with this IP address.")
    
