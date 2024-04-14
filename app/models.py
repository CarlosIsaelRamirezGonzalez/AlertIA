from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from bson import ObjectId
from . import db
from . import login_manager

class User(UserMixin, db.Document):
    username = db.StringField(required=True)
    email = db.StringField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    
    @property
    def password(self): # Es un metodo disfrazado del atributo password, por ende cuando se invoque el obj.password arrojara el error
        raise AttributeError("password is not readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=ObjectId(user_id)).first()

class Notification(db.Document):
    user = db.StringField(required=True)
    date_time = db.DateTimeField(required=True)
    place = db.StringField(required=True)
    threat = db.StringField(required=True)
    camera_name = db.StringField(required=True)
    certainty = db.StringField(required=True)
    image = db.BinaryField(required=True)