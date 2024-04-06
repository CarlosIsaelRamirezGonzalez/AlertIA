from flask_login import UserMixin
from bson import ObjectId
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from . import db
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=ObjectId(user_id)).first()

class User(UserMixin, db.Document):
    username = db.StringField(required=True)
    email = db.StringField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    confimed = db.StringField(db.Boolean)
    
    @property
    def password(self):
        raise AttributeError("password is not readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def generate_confirmation_token(self, expiration=300):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    
    def __repr__(self):
        return '<User %r>' % self.username
    
