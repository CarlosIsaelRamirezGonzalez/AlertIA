# import libreries
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from config import config

# Assign variables to classes
bootstrap = Bootstrap()
db = MongoEngine()
login_manager = LoginManager()
mail = Mail()

# set an endpoint
login_manager.login_view = 'auth.login'

# set a message when the user try to go to a protected view
login_manager.login_message = "Please log in before accesing this page."

# Create the app function
def create_app(config_name):
    app = Flask(__name__)
    
    # Get the global config
    app.config.from_object(config[config_name])
    
    # initialize  the classes
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    
    # Register blue prints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    
    from .alert import alert as alert_blueprint
    app.register_blueprint(alert_blueprint, url_prefix="/alert")
    
    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)
    
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from .help import help as help_blueprint
    app.register_blueprint(help_blueprint, url_prefix='/help')
    
    return app
    