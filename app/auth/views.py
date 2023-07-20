from . import auth
from itsdangerous import URLSafeSerializer
from app.mongo_service import existing_email, insert_user, get_pasword, get_username
from app.forms import SignupForm, LoginForm
from app.helpers import send_message, generate_token
from app.models import UserData, UserModel
from flask import render_template, url_for, redirect, flash
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
    
    

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()
    token = None
    
    if signup_form.validate_on_submit():
        username = signup_form.username.data
        email = signup_form.email.data
        password = signup_form.password.data
        
        user_doc = existing_email(email)
        
        if user_doc is None:
            password_hash = generate_password_hash(password)
            user_data = UserData(username, password_hash, email)
            token = generate_token(username, password)
            send_message(email, token)
            insert_user(user_data)
            user = UserModel(user_data)
            login_user(user)
            return redirect(url_for('WelcomePage'))
        else:
            flash('El email ya existe')
    
    context = {
        'signup_form' : signup_form,
        'token' : token
    }
            
    return render_template('signup.html', **context)
