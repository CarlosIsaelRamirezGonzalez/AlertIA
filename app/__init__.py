from flask import Flask
from .config import Config
from flask_login import LoginManager
from flask_mail import Mail
from .auth import auth
from .cameras import cameras
from .models import UserModel

login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'

@login_manager.user_loader
def load_user(email):
    user_model = UserModel()
    return user_model.query(email)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    login_manager.init_app(app)
    mail = Mail(app)
    app.register_blueprint(auth)
    app.register_blueprint(cameras)
    return app
