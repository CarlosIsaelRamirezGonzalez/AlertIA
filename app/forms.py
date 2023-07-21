from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class SignupForm(FlaskForm):
    username = StringField('User name', validators=[DataRequired(message="Te falta llenar este campo"), Length(min=5,max=15)])
    email = StringField('Email', validators=[DataRequired(), Email(message="Ingresa un correo valido")])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmation_password = PasswordField('Confirmation Password', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben ser iguales')])
    submit = SubmitField('Send')
    
class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Send')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="Ingresa un correo valido")])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Send')

class TokenForm(FlaskForm):
    token = StringField('Token', validators=[DataRequired()])
    submit = SubmitField('Send')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben ser iguales')])
    submit = SubmitField('Send')