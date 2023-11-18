from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
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
    
class WebCameraForm(FlaskForm):
    address = StringField('Direccion', validators=[
        DataRequired(message="Por favor, ingresa la direccion.")
    ])
    place = SelectField('Sitio', choices=[('personalized', 'Personalizado'),
                                          ('home', 'Casa'), ('building', 'Edificio'),
                                          ('square', 'Plaza'),('street', 'Calle')])
    camera_name = StringField('Nombre de la camara', validators=[
        DataRequired(message="Por favor ingresa un nombre para la camara."),
        Length(max=20, message="El nombre es demasiado largo")
    ])
    phone_number = StringField('Numero de telefono', validators=[
        DataRequired(message="Por favor ingrese un numero de telefono."),
        Length(min=10, message="Ingrese un numero de telefono valido.")
    ])
    fires = BooleanField('Incendios')
    bladed_weapons = BooleanField('Arma blanca')
    stabbing = BooleanField('Apuñalamiento')
    handgun = BooleanField('Armas cortas')
    long_gun = BooleanField('Armas largas')
    brandishing = BooleanField('Encañonamiento')
    dog_aggresion = BooleanField('Ataque de perro')
    car_accident = BooleanField('Accidente de coche')
    brawls = BooleanField('Peleas')
    injured_people = BooleanField('Personas heridas')
    submit = SubmitField('Confirmar') 


class SecurityCameraForm(WebCameraForm):
    ip_address = StringField("IP", validators=[
        DataRequired(message="Ingrese la direccion IP."),
        Regexp(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
               message="Ingrese una direccion IP valida.")
    ])
    
class ResetPasswordForm(FlaskForm):
    """ 
    Formulario para restablecer la contraseña.
    """
    confirm_password = PasswordField('Confirmar contraseña', validators=[
        DataRequired(message="Por favor, confirma la contraseña."), 
        EqualTo('password', message='Las contraseñas deben coincidir.')
        ])
    
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
