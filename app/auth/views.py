from . import auth
from datetime import datetime, timedelta, timezone
from app.forms import SignupForm, LoginForm, TokenForm, ResetPasswordForm, EmailForm
from app.helpers import send_message, generate_token, delete_sessions
from app.models import UserData, UserModel
from flask import render_template, url_for, redirect, flash, session
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash

@auth.route('/login', methods=['GET','POST'])
def login_page():
    login_form = LoginForm()
    user_model = UserModel()
    context = {
        'login_form': login_form
    }
    
    if login_form.validate_on_submit():
        
        email = login_form.email.data
        password = login_form.password.data
        user_doc = user_model.get_password(email)
        
        if user_doc is not None:
            
            password_hash = user_doc['password']
            
            if check_password_hash(password_hash, password):
                
                if user_model.check_admin(email) is True:
                    return redirect(url_for('supervisorCameraPanel'))

                username = user_model.get_username(email)
                user_data = UserData(username, password_hash, email)
                    
                user = UserModel(user_data)
                login_user(user)
                return redirect(url_for('WelcomePage'))
        
        flash('Hubo un error con los datos proporcionados')
        
    return render_template('login.html', **context)
    
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()
    user_model = UserModel()

    context = {
        'signup_form' : signup_form,
    }
    
    if signup_form.validate_on_submit():
        username = signup_form.username.data
        email = signup_form.email.data
        password = signup_form.password.data
        
        user_doc = user_model.existing_email(email)
        
        if user_doc is None:
            token = generate_token(email, password, username)
    
            send_message(email, token, username)
            
            session['username'] = username
            session['email'] = email
            session['password'] = password 
            session['token'] = token   
            session['token_timestap'] = datetime.now(timezone.utc).astimezone(timezone.utc)
            session['action'] = "Signup"
                        
            return redirect(url_for('auth.token_validation'))
        else:
            flash('El email ya existe')            
    return render_template('signup.html', **context)


@auth.route('/TokenValidation', methods=['GET', 'POST'])
def token_validation():
    # Verificamos si el valor 'action' está almacenado en la sesión
    if not session.get('action'):
        flash('Acceso no autorizado.', 'error-message')
        return(url_for('index'))
    # Obtenemos el form
    token_form = TokenForm()
    # Obtenemos los valores guardados en la sesión
    username = session.get('username')
    email = session.get('email')
    password = session.get('password')
    token = session.get('token')
    token_timestap = session.get('token_timestap')
    action = session.get('action')
    
    context = {
        'token_form': token_form, 
        'email': session.get('email')
    }
    
    if token_form.validate_on_submit():
        # Tomamos el tiempo de creacion de el token y el tiempo transcurrido
        current_time = datetime.now(timezone.utc)
        token_timestap = token_timestap.replace(tzinfo=timezone.utc)
        #Accion si el usuario viene del registro
        if current_time > token_timestap + timedelta(minutes=3):
            flash('El token ha caducado. Por favor intentelo nuevamente')
            # Aqui redirigimos al usuario dependiendo de que view llego
            if action == 'Signup': 
                return redirect(url_for('auth.signup'))
            else:
                return redirect(url_for('auth.login_page'))
        # Verificamos que el token ingresado sea el mismo que el enviado
        user_token = token_form.token.data
        if token == user_token:
            if action== "Signup":
                # Encriptamos el password
                password_hash = generate_password_hash(password)
                user_data = UserData(username, password_hash, email)
                user = UserModel(user_data)
                user.insert_user(user_data)
                login_user(user)
                # Liberamos las cookies del usuario
                delete_sessions(['email', 'password', 'username', 'token_timestap', 'token', 'action'])
                # Redirección después de un registro exitoso
                return redirect(url_for('WelcomePage'))
            else:
                # Agregamos una nueva cookie 
                session['token_verified'] = True
                # Liberamos las cookies del usuario
                delete_sessions(['token_timestap', 'token', 'action'])
                # Redirección después de una validación de token exitosa
                return redirect(url_for('auth.reset_password'))
        else:
            flash('El token que ingreso no coincide', 'error')
    return render_template('tokenValidation.html', **context)



@auth.route('/ForgotPassword', methods=['GET', 'POST'])
def restore_password():
    email_form = EmailForm()
    user_model = UserModel()
    context = {
        'email_form': email_form
    }
    if email_form.validate_on_submit():
        email = email_form.email.data 
        user_doc = user_model.existing_email(email)
        if user_doc:
            token = generate_token(email, user_doc['password'], user_doc['username']) # User_doc['password']?
            send_message(email, token, user_doc['username'], "Forgot password")
            session['email'] = email
            session['token'] = token
            session['action'] = "Restore"
            session['token_timestap'] = datetime.now(timezone.utc).astimezone(timezone.utc)
            return redirect(url_for('auth.token_validation'))
        else:
            flash("Ese email no existe.")
    return render_template('forgotpassword.html', **context)
            

            
@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    
    if 'token_verified' not in session:
        flash('Primero debes ingresar tu correo electrónico y validar el token.', 'error')
        return redirect(url_for('auth.restore_password'))
    reset_form = ResetPasswordForm()
    user_model = UserModel()
    
    context = {
        'reset_form' : reset_form
    }
    
    email = session['email']
    
    if reset_form.validate_on_submit():
        new_password = reset_form.password.data 
        
        password_hash = generate_password_hash(new_password)
        user_model.update_password(email=email, password=password_hash)
        
        flash("Tu contraseña ha sido restaurada exitosamenre")
        delete_sessions(['email', 'token_verified'])
        
        return redirect(url_for('auth.login_page'))
    
    return render_template('restorepassword.html', **context)