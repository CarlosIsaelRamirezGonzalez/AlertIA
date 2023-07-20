from flask import Flask
from .config import Config
from flask_login import LoginManager
from flask_mail import Mail
from .auth import auth
from .models import UserModel

login_manager = LoginManager()
login_manager.login_view = 'auth.LoginPage'

@login_manager.user_loader
def load_user(username):
    return UserModel.query(username)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    login_manager.init_app(app)
    mail = Mail(app)
    app.register_blueprint(auth)
    return app
