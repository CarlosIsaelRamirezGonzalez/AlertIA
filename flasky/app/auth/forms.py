from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..models import User

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 64)])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,  'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 64), EqualTo('password2', message=('Passwords must match.'))])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    
    # validate methods
    def validate_email(self, field): #Campo email field.data = email
        if User.objects(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.objects(username=field.data).first():
            raise ValidationError('Username already in use.')   

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 64)])
    remember_me = BooleanField('Keep me logged in')    
    