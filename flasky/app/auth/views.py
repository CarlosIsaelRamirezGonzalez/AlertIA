from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeSerializer as Serializer
import random
import datetime
from . import auth
from .forms import LoginForm, SignupForm, TokenForm, PasswordResetRequestForm, ResetPasswordForm
from ..models import User
from ..email import send_email

@auth.before_app_request
def before_app_request():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.blueprint != 'auth' \
        and request.blueprint != 'main' \
        and request.blueprint != 'admin' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))
    

    
    
    
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    
    form = SignupForm()
    
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data)
        user.password = form.password.data
        user.save()
        login_user(user)
        print(current_app.config['FLASKY_ADMIN'])
        if user.email == current_app.config['FLASKY_ADMIN']:
            return redirect(url_for('admin.cameras_panel'))

        token = current_user.generate_confirmation_token()
        session[token] = datetime.datetime.now() + datetime.timedelta(minutes=3) 
        send_email(current_user.email, 'Confirm your account.', 'auth/email/confirm', user=current_user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.check'))        
    
    return render_template('auth/signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    
    form = LoginForm()
    
    # random phrases with icons -- Cambiar a un .txt
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

            if not user.confirmed:
                token = user.generate_confirmation_token()
                session[token] = datetime.datetime.now() + datetime.timedelta(minutes=3) 
                send_email(user.email, 'Confirm your account.', 'auth/email/confirm', user=user, token=token)
                flash('A confirmation email has been sent to you by email.')
                
                return redirect(url_for('auth.check'))
        
            if user.email == current_app.config['FLASKY_ADMIN']:
                return redirect(url_for('admin.cameras_panel'))
                
            next = request.args.get('next') # Get where the user try to go 
            
            # Protect the user from a possible scam
            if next is None or not next.startswith('/'):
                next = url_for('home.index')
                
            return redirect(next)
        
        flash('Invalid username or password')
        
    return render_template('auth/login.html', form=form, phrase=phrase, icon=icon)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/check', methods=['GET', 'POST'])
def check():
    form = TokenForm()
    if form.validate_on_submit():
        s = Serializer(current_app.config['SECRET_KEY'])
        encrypt_token = s.dumps({'token' : form.token.data})
        
        if session['Reset_Password']:
            return redirect(url_for('auth.password_token', token=encrypt_token, email = session['Reset_Password_Email'], _external=True ))
        
        return redirect(url_for('auth.confirm', token=encrypt_token, _external=True))
        
    return render_template('auth/check.html', form=form)


@auth.route('/confirm/<token>/<email>', methods=['GET', 'POST'])
def password_token(token, email):
    user = User.objects(email=email).first()
    if user and user.confirm_token(token):
        login_user(user)
        return(redirect(url_for('auth.password_reset')))
                
    else:
        flash("The confirmation token is invalid or has expired.")
        
@auth.route('/password_reset', methodss=['GET', 'POST'])
@login_required
def password_reset():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        current_user.reset_password(password=form.password.data)
        flash('Your password has been updated.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/change-password.html')
        

@auth.route('/confirm/<token>', methods=['GET', 'POST'])
@login_required
def confirm(token):
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
    token = current_user.generate_confirmation_token()
    session[token] = datetime.datetime.now() + datetime.timedelta(minutes=3) 
    send_email(current_user.email, 'Confirm your account.', 'auth/email/confirm', user=current_user, token=token)
    flash('A confirmation email has been sent to you by email.')
    return redirect(url_for('auth.check'))
    
    

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user =  User.objects(email = form.email.data).first()
        token = user.generate_confirmation_token()
        session[token] = datetime.datetime.now() + datetime.timedelta(minutes=3) 
        session["Reset_Password"] = True
        session["Reset_Password_Email"] = user.email
        send_email(user.email, 'Confirm your account.', 'auth/email/reset_password', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.check'))        
    return render_template('auth/reset-password-email.html', form=form)