from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
import random
import datetime
from . import auth
from .forms import LoginForm, SignupForm
from ..models import User
from ..email import send_email

@auth.before_app_request
def before_app_request():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.blueprint != 'auth' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    
    form = SignupForm()
    
    if form.validate_on_submit():
        
        # Create the user object 
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        
        # Save in database
        user.save()
        
        # generate token
        token = user.generate_confirmation_token()
        
        # Save the token like a key and token expiration like value
        session[token] = datetime.datetime.now() + datetime.timedelta(minutes=3) 
        
        send_email(user.email, 'Confirm your account.', 'auth/email/confirm', user=user, token=token)
        
        return redirect(url_for('auth.token'))        
    
    return render_template('auth/signup.html', form=form)




@auth.route('/token', methods=['GET', 'POST'])
def token():
    return render_template('auth/token.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    
    
    form = LoginForm()
    
    # random phrases with icons
    phrases_icons = {
        "Did you know that Alert AI can detect more than 10 different accidents?" : "fa-solid fa-globe info-icon",
        'The name of our AI is "alertito"' : "fa-solid fa-robot info-icon",
        'Alertito cannot differentiate between an aggressive bite and a gentle bite' : "fa-solid fa-dog info-icon",
        'All your data is encrypted'  : "fa-solid fa-shield-halved info-icon",
        'AlertAI was developed by just two programmers' : "fa-solid fa-user-group info-icon",
        'AlertAI remains active 24 hours a day' : "fa-solid fa-eye info-icon"
    }
    
    # Take a random value
    phrase, icon = random.choice(list(phrases_icons.items()))
    
    if form.validate_on_submit():
        
        user = User.objects(email=form.email.data).first()
        
        # if user exists and passsword is correct
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data) #Register the user 
            next = request.args.get('next') # Get where the user try to go 
            
            # Protect the user from a possible scam
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
                
            return redirect(next)
        
        flash('Invalid username or password')
        
    return render_template('auth/login.html', form=form, phrase=phrase, icon=icon)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

