import os 

class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Hard to guess'
    REMEMBER_COOKIE_DURATION = int(os.environ.get('REMEMBER_COOKIE_DURATION', 10 * 24 * 3600)) 
    PYTHONDONTWRITEBYTECODE = 1 
    
    
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