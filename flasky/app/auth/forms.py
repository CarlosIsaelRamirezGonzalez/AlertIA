"""Formularios de cuentas."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

from ..models import User

USERNAME_PATTERN = r'^[A-Za-z][A-Za-z0-9_.]*$'
# Al menos 8 caracteres, con mayúscula, minúscula, número y símbolo.
STRONG_PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'


class SignupForm(FlaskForm):
    """Registro de una cuenta nueva."""

    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 64)])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp(USERNAME_PATTERN, 0, 'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(1, 64),
        EqualTo('password2', message='Passwords must match.'),
        Regexp(STRONG_PASSWORD_PATTERN, 0, 'Password must contain at least 8 characters, including an uppercase letter, a lowercase letter, a number, and a symbol.')
    ])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])

    def validate_email(self, field):
        """Rechaza un correo ya registrado.

        Args:
            field: Campo del correo.

        Raises:
            ValidationError: Si el correo ya existe.
        """
        if User.objects(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """Rechaza un nombre de usuario ya en uso.

        Args:
            field: Campo del nombre.

        Raises:
            ValidationError: Si el nombre ya existe.
        """
        if User.objects(username=field.data).first():
            raise ValidationError('Username already in use.')


class LoginForm(FlaskForm):
    """Inicio de sesión."""

    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 64)])
    remember_me = BooleanField('Keep me logged in')


class TokenForm(FlaskForm):
    """Código de confirmación que llegó por correo."""

    token = StringField()


class ResetPasswordForm(FlaskForm):
    """Contraseña nueva."""

    password = PasswordField(validators=[DataRequired(), Length(1, 64), EqualTo("password2", message='Passwords must match.')])
    password2 = PasswordField(validators=[DataRequired()])


class PasswordResetRequestForm(FlaskForm):
    """Correo de la cuenta cuya contraseña se quiere cambiar."""

    email = StringField(validators=[DataRequired(), Email()])

    def validate_email(self, field):
        """Rechaza un correo que no está registrado.

        Args:
            field: Campo del correo.

        Raises:
            ValidationError: Si el correo no existe.
        """
        if not User.objects(email=field.data).first():
            raise ValidationError("This email doesn't exists in the system.")
