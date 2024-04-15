import os 

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Hard to guess')
    REMEMBER_COOKIE_DURATION = int(os.environ.get('REMEMBER_COOKIE_DURATION', 10 * 24 * 3600)) 
    MAIL_SERVER = os.environ.get('EMAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[AlertAI]'
    FLASKY_MAIL_SENDER = 'AlertAI Admin <alertia2023@gmail.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True   
    MONGODB_SETTINGS = {
        'host' : os.environ.get('MONGODB_SETTINGS') or 'localhost',
        'db' : 'development_db',
        'port' : 27017
    }

class TestingConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = {
        'host' : os.environ.get('MONGODB_SETTINGS') or 'localhost',
        'db' : 'testing_db',
        'port' : 27017
    }
    
class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'host' : os.environ.get('MONGODB_SETTINGS') or 'localhost',
        'db' : 'production_db',
        'port' : 27017
    }
    
    
config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig
}