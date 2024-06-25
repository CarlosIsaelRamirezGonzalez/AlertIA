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
    place_default = db.StringField(required = True)
    address = db.StringField(required=True)
    latitude = db.FloatField()
    longitude = db.FloatField()
    device_id = db.StringField()
    registered = db.StringField()
    
    
    user = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    alerts = db.IntField(required=True)
    alerts_default = db.IntField(required=True)
    
    
    def __init__(self, **kargs):
        super(Camera, self).__init__(**kargs)
        if self.user is None:
            self.user = current_user.id
    
    def __repr__(self):
        return '<Camera %r>' % self.name
    
    def insert_personalized_alerts(self, form):
        calculated_value = 0
        
        if form.fires.data:
            calculated_value = 1
        
        values = [form.bladed_weapon.data, form.stabbing.data, form.handgun.data, 
                form.long_gun.data, form.cannoning.data, form.dog_attack.data, 
                form.car_accident.data, form.brawls.data, form.injured_people.data]
        
        for i, val in enumerate(values):
            if val:
                calculated_value += 2 ** i    
        
        self.alerts = calculated_value
 
    def insert_place_alerts(self, place):
        match place:
            case "Home": self.alerts = 629
            case "Building": self.alerts = 871
            case "Square":  self.alerts = 883
            case "Street": self.alerts = 1007



    def has_alert(self, alert):
        return self.alerts & alert == alert 
    
    def add_alert(self, alert):
        if not self.has_alert(alert):
            self.alerts += alert

    def remove_alert(self, alert):
        if self.has_alert(alert):
            self.alerts -= alert 
    
    def reset_alerts(self):
        self.alerts = 0   
        
    def get_alerts(self):
        alert_dict = {
            'FIRES': Alerts.FIRES,
            'BLADED_WEAPON': Alerts.BLADED_WEAPON,
            'STABBING': Alerts.STABBING,
            'HANDGUN': Alerts.HANDGUN,
            'LONG_GUN': Alerts.LONG_GUN,
            'CANNONING': Alerts.CANNONING,
            'DOG_ATTACK': Alerts.DOG_ATTACK,
            'CAR_ACCIDENT': Alerts.CAR_ACCIDENT,
            'BRAWLS': Alerts.BRAWLS,
            'INJURED_PEOPLE': Alerts.INJURED_PEOPLE
        }
        active_alerts = []
        for alert_name, alert_value in alert_dict.items():
            if self.alerts & alert_value == alert_value:
                active_alerts.append(alert_name)
        return active_alerts

class Alerts: 
    FIRES = 1
    BLADED_WEAPON = 2
    STABBING = 4
    HANDGUN = 8
    LONG_GUN = 16
    CANNONING = 32
    DOG_ATTACK = 64
    CAR_ACCIDENT = 128
    BRAWLS = 256
    INJURED_PEOPLE = 512
    
    
class Report(db.Document):
    title = db.StringField()
    body = db.StringField()
    label = db.StringField(required=True)
    date_time = db.DateTimeField(required=True)
    user = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    camera = db.ReferenceField(Camera, reverse_delte_rule=db.CASCADE)
    image = db.BinaryField(required=True)
    
