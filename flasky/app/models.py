from flask_login import UserMixin
from bson import ObjectId
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, session, flash
from datetime import datetime, timedelta, timezone
import hashlib
from . import db
from . import login_manager
import random

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=ObjectId(user_id)).first()

class User(UserMixin, db.Document):
    username = db.StringField(required=True)
    email = db.StringField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    confimed = db.BooleanField(default=False)
    
    @property
    def password(self):
        raise AttributeError("password is not readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def generate_confirmation_token(self):
        data_token = f'{self.email}{self.password_hash}{self.username}'.encode('utf-8')
        hash_result = hashlib.sha256(data_token).hexdigest()
        token = hash_result[:4]
        num_random = random.randint(100, 999)
        return token + str(num_random)


    def confirm_token(self, token):
        token_generated_time = session.get(token)
        if token_generated_time:
            current_time = datetime.now(timezone.utc)
            token_timestap = token_timestap.replace(tzinfo=timezone.utc)
            
            if current_time > token_timestap + timedelta(minutes=3):
                flash('The token has expired')
                return 
            
            self.confirmed = True
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<User %r>' % self.username
    
