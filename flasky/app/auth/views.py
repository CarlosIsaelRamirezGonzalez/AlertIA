"""Vistas de cuentas: registro, sesión, confirmación por código y cambio de contraseña."""

from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeSerializer as Serializer
import random
import datetime
from . import auth
from .forms import LoginForm, SignupForm, TokenForm, PasswordResetRequestForm, ResetPasswordForm
from ..models import User
from ..email import send_email
from ..schemas import LoginTip

TOKEN_MINUTES = 3

# Datos curiosos de la pantalla de inicio de sesión; se muestra uno al azar.
LOGIN_TIPS = (
    LoginTip(text="Did you know that Alert AI can detect more than 10 different accidents?", icon="fa-solid fa-globe info-icon"),
    LoginTip(text='The name of our AI is "alertito"', icon="fa-solid fa-robot info-icon"),
    LoginTip(text='Alertito cannot differentiate between an aggressive bite and a gentle bite', icon="fa-solid fa-dog info-icon"),
    LoginTip(text='All your data is encrypted', icon="fa-solid fa-shield-halved info-icon"),
    LoginTip(text='AlertAI was developed by just two programmers', icon="fa-solid fa-user-group info-icon"),
    LoginTip(text='AlertAI remains active 24 hours a day', icon="fa-solid fa-eye info-icon"),
)


def send_token(user, subject, template):
    """Genera un código, guarda su vencimiento en la sesión y lo manda por correo.

    Args:
        user: Usuario que recibe el código.
        subject: Asunto del correo.
        template: Plantilla del correo, sin extensión.
    """
    token = user.generate_confirmation_token()
    session[token] = datetime.datetime.now() + datetime.timedelta(minutes=TOKEN_MINUTES)
    send_email(user.email, subject, template, user=user, token=token)

@auth.before_app_request
def before_app_request():
    """Manda a confirmar el correo a quien inició sesión sin confirmarlo.

    Returns:
        Una redirección, o None para seguir con la página pedida.
    """
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.blueprint != 'auth' \
        and request.blueprint != 'main' \
        and request.blueprint != 'admin' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))
    

    
    
    
@auth.route('/unconfirmed')
def unconfirmed():
    """Pide confirmar la cuenta.

    Returns:
        La página, o una redirección si no hace falta.
    """
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """Registra una cuenta e inicia su sesión; manda el código de confirmación por correo.

    Returns:
        El formulario, o una redirección a la pantalla del código.
    """
    
    form = SignupForm()
    
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data)
        user.password = form.password.data
        user.save()
        login_user(user)
        if user.email == current_app.config['FLASKY_ADMIN']:
            return redirect(url_for('admin.cameras_panel'))

        send_token(current_user, 'Confirm your account.', 'auth/email/confirm')
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.check')) 
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'error')      
    
    return render_template('auth/signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Inicia sesión. Si la cuenta no está confirmada, manda otro código.

    Returns:
        El formulario, o una redirección a la página que se quería ver.
    """
    
    form = LoginForm()
    
    tip = random.choice(LOGIN_TIPS)

    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)

            if not user.confirmed:
                send_token(user, 'Confirm your account.', 'auth/email/confirm')
                flash('A confirmation email has been sent to you by email.')
                
                return redirect(url_for('auth.check'))
        
            if user.email == current_app.config['FLASKY_ADMIN']:
                return redirect(url_for('admin.cameras_panel'))
                
            # A dónde quería ir; solo se aceptan rutas internas, para no redirigir a otro sitio.
            next_page = request.args.get('next')
            
            if next_page is None or not next_page.startswith('/') or next_page.startswith('//'):
                next_page = url_for('home.index')
            return redirect(next_page)
        
        flash('Invalid username or password')
        
    return render_template('auth/login.html', form=form, phrase=tip.text, icon=tip.icon)

@auth.route('/logout')
@login_required
def logout():
    """Cierra la sesión.

    Returns:
        Una redirección a la página de inicio.
    """
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/check', methods=['GET', 'POST'])
def check():
    """Recibe el código del correo, lo firma y lo manda a validar.

    Returns:
        El formulario, o una redirección a la confirmación o al cambio de contraseña.
    """
    form = TokenForm()
    if form.validate_on_submit():
        serializer = Serializer(current_app.config['SECRET_KEY'])
        encrypt_token = serializer.dumps(form.token.data)
        
        if session.get('reset_password') == True:
            return redirect(url_for('auth.password_token', token=encrypt_token, email = session.get('reset_password_email'), _external=True ))
        
        return redirect(url_for('auth.confirm', token=encrypt_token, _external=True))
        
    return render_template('auth/check.html', form=form)


@auth.route('/confirm/<token>/<email>', methods=['GET', 'POST'])
def password_token(token, email):
    """Valida el código de cambio de contraseña e inicia la sesión para cambiarla.

    Args:
        token: Código firmado.
        email: Correo de la cuenta.

    Returns:
        Una redirección al cambio de contraseña, o de vuelta al código si no es válido.
    """
    user = User.objects(email=email).first()
    if user and user.confirm_token(token):
        login_user(user)
        session['reset_password'] = False
        return(redirect(url_for('auth.password_reset')))
                
    flash("The confirmation token is invalid or has expired.")
    return redirect(url_for('auth.check'))


@auth.route('/password_reset', methods=['GET', 'POST'])
@login_required
def password_reset():
    """Cambia la contraseña del usuario de la sesión.

    Returns:
        El formulario, o una redirección al inicio de sesión.
    """
    form = ResetPasswordForm()
    if form.validate_on_submit():
        current_user.reset_password(new_password=form.password.data)
        flash('Your password has been updated.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/change-password.html', form=form)
        

@auth.route('/confirm/<token>', methods=['GET', 'POST'])
@login_required
def confirm(token):
    """Confirma la cuenta con un código firmado.

    Args:
        token: Código firmado.

    Returns:
        Una redirección según el resultado.
    """
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    
    if current_user.confirm_token(token):
        flash('You have confirmed your account. Thanks!')
        return (redirect(url_for('home.index')))
    else:   
        flash('The confirmation token is invalid or has expired.')
        
    return (redirect(url_for('auth.check')))

@auth.route('/confirm')
@login_required
def resend_confirmation():
    """Manda otro código de confirmación.

    Returns:
        Una redirección a la pantalla del código.
    """
    send_token(current_user, 'Confirm your account.', 'auth/email/confirm')
    flash('A confirmation email has been sent to you by email.')
    return redirect(url_for('auth.check'))
    
    

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """Manda un código para cambiar la contraseña.

    Returns:
        El formulario, o una redirección a la pantalla del código.
    """
    
    if not current_user.is_anonymous:
        logout_user()
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user =  User.objects(email = form.email.data).first()
        # Mismo mensaje exista o no la cuenta: así no se revela qué correos están registrados.
        if user is None:
            flash('A reset password email has been sent to you by email.')
            return redirect(url_for('auth.check'))
        session["reset_password"] = True
        session["reset_password_email"] = user.email
        send_token(user, 'Reset the password.', 'auth/email/reset_password')
        flash('A reset password email has been sent to you by email.')
        return redirect(url_for('auth.check'))        
    return render_template('auth/reset-password-email.html', form=form)