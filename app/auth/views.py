from . import auth
from datetime import datetime, timedelta, timezone
from app.mongo_service import existing_email, insert_user, get_pasword, get_username
from app.forms import SignupForm, LoginForm, TokenForm
from app.helpers import send_message, generate_token
from app.models import UserData, UserModel
from dateutil.parser import parse
from flask import render_template, url_for, redirect, flash, session
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash

@auth.route('/login', methods=['GET','POST'])
def LoginPage():
    login_form = LoginForm()
    
    context = {
        'login_form': login_form
    }
    
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user_doc = get_pasword(email)
        
        if user_doc is not None:
            password_hash = user_doc['password']
            if check_password_hash(password_hash, password):
                username = get_username(email)
                user_data = UserData(email, password, username)
                
                user = UserModel(user_data)
                login_user(user)
                return redirect(url_for('WelcomePage'))
            
            else:
                flash('EL error radica en la contraseña')
        flash('Hay algo mal en los datos')
        
    return render_template('login.html', **context)
    
    
@auth.route('/TokenValidation', methods=['GET', 'POST'])
def token_validation():
    token_form = TokenForm()

    username = session.get('username')
    email = session.get('email')
    password = session.get('password')
    token = session.get('token')
    token_timestap = session.get('token_timestap')
    
    context = {
        'token_form': token_form, 
        'email': email
    }
    
    if token_form.validate_on_submit():
        
        current_time = datetime.now(timezone.utc)
        token_timestap = token_timestap.replace(tzinfo=timezone.utc)
        
        if current_time > token_timestap + timedelta(minutes=3):
            flash('El token ha caducado. Por favor regsistrese nuevamente')
            return redirect(url_for('auth.signup'))
        
        user_token = token_form.token.data
        if token == user_token:
            password_hash = generate_password_hash(password)
            user_data = UserData(username, password_hash, email)
            insert_user(user_data)
            user = UserModel(user_data)
            login_user(user)
            return redirect(url_for('WelcomePage'))
        else:
            flash('El token que ingreso no coincide', 'error')
    return render_template('tokenValidation.html', **context)
            



@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()
    context = {
        'signup_form' : signup_form,
    }
    
    if signup_form.validate_on_submit():
        username = signup_form.username.data
        email = signup_form.email.data
        password = signup_form.password.data
        
        user_doc = existing_email(email)
        
        if user_doc is None:
            token = generate_token(email, password, username)
    
            send_message(email, token)
            
            session['username'] = username
            session['email'] = email
            session['password'] = password 
            session['token'] = token   
            session['token_timestap'] = datetime.now(timezone.utc).astimezone(timezone.utc)

                        
            return redirect(url_for('auth.token_validation'))
        else:
            flash('El email ya existe')            
    return render_template('signup.html', **context)