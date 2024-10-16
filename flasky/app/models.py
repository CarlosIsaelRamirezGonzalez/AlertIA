from flask_login import UserMixin, current_user
from bson import ObjectId
from itsdangerous import URLSafeSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, flash, current_app
from datetime import datetime
import hashlib
from . import db
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=ObjectId(user_id)).first()

class User(UserMixin, db.Document):
    username = db.StringField(required=True)
    email = db.StringField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    available = db.BooleanField(default=True)
    confirmed = db.BooleanField(default=False)
    
    def __init__(self, **kargs):
        super(User, self).__init__(**kargs)
        if self.email == current_app.config['FLASKY_ADMIN']:
            self.confirmed = True
    
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
        token = hash_result[:10]
        token = token.upper()
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
    
    def reset_password(self, new_password):
        self.password = new_password
        self.save()
    
    def __repr__(self):
        return '<User %r>' % self.username
    
class Notification(db.Document):
    user = db.StringField(required=True) #Corregir esto ¿Por que no conecta directamente con un usuario?
    date_time = db.DateTimeField(required=True)
    place = db.StringField(required=True)
    threat = db.StringField(required=True)
    camera_name = db.StringField(required=True)
    certainty = db.StringField(required=True)
    image = db.BinaryField(required=True)
    read = db.BooleanField(default=False)
    starred = db.BooleanField(default=False)
     

class Camera(db.Document):
    name = db.StringField(required=True)
    phone_number = db.StringField(required=True)
    camera_type = db.StringField(required=True)
    url = db.StringField()
    place = db.StringField(required=True, choices=["Home", "Building", "Square", "Street", "Personalized"])
    place_default = db.StringField(required=True)
    address = db.StringField(required=True)
    latitude = db.StringField()
    longitude = db.StringField()
    device_id = db.StringField()
    registered = db.StringField()

    user = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    alerts = db.ListField(db.StringField(), required=True)
    alerts_default = db.ListField(db.StringField(), required=True)

    def __init__(self, **kargs):
        super(Camera, self).__init__(**kargs)
        if self.user is None:
            self.user = current_user.id

    def __repr__(self):
        return '<Camera %r>' % self.name

    def insert_personalized_alerts(self, form):
        self.alerts = []
        alert_fields = {
            'fires': form.fires.data,
            'bladed_weapon': form.bladed_weapon.data,
            'stabbing': form.stabbing.data,
            'handgun': form.handgun.data,
            'long_gun': form.long_gun.data,
            'cannoning': form.cannoning.data,
            'dog_attack': form.dog_attack.data,
            'car_accident': form.car_accident.data,
            'brawls': form.brawls.data,
            'injured_people': form.injured_people.data
        }
        
        for alert, active in alert_fields.items():
            if active:
                self.alerts.append(alert)
    
    def insert_place_alerts(self, place):
        place_alerts = {
            "Home": [Alerts.FIRES, Alerts.BLADED_WEAPON, Alerts.STABBING, Alerts.HANDGUN, Alerts.DOG_ATTACK],
            "Building": [Alerts.FIRES, Alerts.BLADED_WEAPON, Alerts.HANDGUN, Alerts.LONG_GUN, Alerts.CAR_ACCIDENT],
            "Square": [Alerts.FIRES, Alerts.BLADED_WEAPON, Alerts.HANDGUN, Alerts.LONG_GUN, Alerts.DOG_ATTACK, Alerts.BRAWLS],
            "Street": [Alerts.FIRES, Alerts.BLADED_WEAPON, Alerts.STABBING, Alerts.HANDGUN, Alerts.LONG_GUN, Alerts.CANNONING, Alerts.DOG_ATTACK, Alerts.CAR_ACCIDENT, Alerts.BRAWLS]
        }
        
        self.alerts = place_alerts.get(place, [])

    def has_alert(self, alert):
        return alert in self.alerts

    def add_alert(self, alert):
        if not self.has_alert(alert):
            self.alerts.append(alert)

    def remove_alert(self, alert):
        if self.has_alert(alert):
            self.alerts.remove(alert)

    def reset_alerts(self):
        self.alerts = []

    def get_alerts(self):
        return self.alerts

class Alerts: 
    FIRES = "fires"
    BLADED_WEAPON = "bladed_weapon"
    STABBING = "stabbing"
    HANDGUN = "handgun"
    LONG_GUN = "long_gun"
    CANNONING = "cannoning"
    DOG_ATTACK = "dog_attack"
    CAR_ACCIDENT = "car_accident"
    BRAWLS = "brawls"
    INJURED_PEOPLE = "injured_people"

    @classmethod
    def all_alerts(cls):
        return [
            cls.FIRES, cls.BLADED_WEAPON, cls.STABBING, cls.HANDGUN,
            cls.LONG_GUN, cls.CANNONING, cls.DOG_ATTACK,
            cls.CAR_ACCIDENT, cls.BRAWLS, cls.INJURED_PEOPLE
        ]
    
    
class Report(db.Document):
    title = db.StringField()
    body = db.StringField()
    label = db.StringField(required=True)
    date_time = db.DateTimeField(required=True)
    user = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    camera = db.ReferenceField(Camera, reverse_delte_rule=db.CASCADE)
    image = db.BinaryField(required=True)
    
