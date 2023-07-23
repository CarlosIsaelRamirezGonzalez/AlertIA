from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

class EmailForm(FlaskForm):
    """
    Formulario para ingresar el correo electronico
    """
    email = StringField('Email', validators=[
        DataRequired(message="Por favor ingresa un correo electronico."),
        Email(message="Por favor ingrese ingrese un correo electrónico válido.")
        ])
    
    submit = SubmitField('Send')
    
class LoginForm(FlaskForm):
    """
    Formulario para inicio de sesión.
    """
    email = StringField('Email', validators=[
        DataRequired(message="Por favor ingresa un correo electronico."), 
        Email(message="Por favor ingrese un correo electrónico valido", check_deliverability=True)
        ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="Por favor ingresa una contraseña.")
        ])
    
    submit = SubmitField('Send')
    
class ResetPasswordForm(FlaskForm):
    """ 
    Formulario para restablecer la contraseña.
    """
    confirm_password = PasswordField('Confirmar contraseña', validators=[
    DataRequired(message="Por favor, confirma la contraseña."), 
    EqualTo('password', message='Las contraseñas deben coincidir.')])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="Por favor, ingresa una nueva contraseña."),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d.*\d)(?=.*[@#$%.&*?!])[A-Za-z\d@#$%.&*?!]{5,15}$',
                message="La contraseña debe tener al menos 2 numeros, una letra, uno de los siguientes signos:[@#$%.&*?!] y una longitud de entre 5 y 15.")
        ])
    
    submit = SubmitField('Send')

class SignupForm(FlaskForm):
    """
    Formulario para registrarse.
    """
    confirmation_password = PasswordField('Confirmation Password', validators=[
        DataRequired(message="Por favor, confirme la contraseña."), 
        EqualTo('password', message='Las contraseñas deben ser iguales')
        ])    
    
    email = StringField('Email', validators=[
        DataRequired(message="Por favor, ingrese el correo electronico"),
        Email(message="Por favor, ingrese un correo electronico valido", check_deliverability=True)
        ])
    
    username = StringField('User name', validators=[
        DataRequired(message="Por favor, ingrese el nombre de usuario."), 
        Length(min=5,max=15, message="El nombre de usuario debe tener entre 5 y 15 caracteres.")
        ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="Por favor, ingresa una nueva contraseña."),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d.*\d)(?=.*[@#$%.&*?!])[A-Za-z\d@#$%.&*?!]{5,15}$',
                message="La contraseña debe tener al menos 2 numeros, una letra, uno de los siguientes signos:[@#$.%&*?!] y una longitud de entre 5 y 15.")
        ])
    
    submit = SubmitField('Send')
    
class TokenForm(FlaskForm):
    """ 
    Formulario para ingresar el token
    """
    token = StringField('Token', validators=[
        DataRequired(message="Por favor ingrese el token")
        ])
    submit = SubmitField('Send')
