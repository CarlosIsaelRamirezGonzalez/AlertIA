from flask_login import UserMixin
from bson import ObjectId
from itsdangerous import URLSafeSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, flash, current_app
from datetime import datetime
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
    confirmed = db.BooleanField(default=False)
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
                
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def generate_confirmation_token(self):
        data_token = f'{self.email}{self.password_hash}{self.username}'.encode('utf-8')
        hash_result = hashlib.sha256(data_token).hexdigest()
        token = hash_result[:5]
        return token 



    def confirm_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
                decrypt_token = s.loads(token)
        except:
            return False
        
        decrypt_token = decrypt_token.get('token')
        
        token_expiration_time = session.get(decrypt_token)
        
        # If token exists
        if token_expiration_time:
            current_time = datetime.now()

            if current_time < token_expiration_time:
                
                self.confirmed = True
                # Save the changes in the database
                self.save()
                return True
            
            flash('The token has expired.')
            return False
        
        flash('The token is incorrect')
        return False
        
    
    def __repr__(self):
        return '<User %r>' % self.username
    
class Notification(db.Document):
    user = db.StringField(required=True)
    date_time = db.DateTimeField(required=True)
    place = db.StringField(required=True)
    threat = db.StringField(required=True)
    camera_name = db.StringField(required=True)
    certainty = db.StringField(required=True)
    image = db.BinaryField(required=True)
    read = db.BooleanField(default=False)