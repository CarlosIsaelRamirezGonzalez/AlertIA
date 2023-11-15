from flask_login import UserMixin
from .mongo_service import Database
from bson import ObjectId

class UserData():
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

class UserModel(UserMixin):
    
    def __init__(self, user_data = None):
        db = Database()
        self.users_collection = db.users_collection()
    
        if user_data is not None:
            self.id = user_data.email
            self.password = user_data.password
            self.username = user_data.username
        
    def insert_user(self):
        self.users_collection.insert_one({
            'username': self.username,
            'password': self.password,
            'email': self.id
        })
    
    def update_password(self, email, password):
        self.users_collection.update_one({'email' : email}, {'$set': {'password': password} })

    def get_username(self, email):
        return self.users_collection.find_one({'email': email}, {'_id': 0, 'password': 0, 'email': 0})
        
    def existing_email(self, email):
        return self.users_collection.find_one({'email': email})

    def get_password(self,email):
        return self.users_collection.find_one({'email': email},{'_id': 0, 'email': 0, 'username': 0})

    def check_admin(self, email):
        data = self.users_collection.find_one({'email': email})
        if data is not None and data.get('admin', False):
            return True
        else:
            return False 
    
    def query(self, email):
        user_doc = self.existing_email(email)
        if user_doc is not None:
            user_data = UserData(username=user_doc['username'], password=user_doc['password'], email=user_doc['email'])
            return UserModel(user_data)


class CameraData():
    def __init__(self, user_id, ip, address, place, camera_type, camera_name, settings, phone_number):
        self.user_id = user_id
        self.ip = ip
        self.address = address
        self.place = place
        self.camera_type = camera_type
        self.camera_name = camera_name
        self.settings = settings
        self.phone_number = phone_number

class CameraModel():
    
    def __init__(self, camera_data = None):
        db = Database()
        self.cameras_collection = db.cameras_collection()
        if camera_data is not None:
            self.id = camera_data.user_id
            self.ip = camera_data.ip
            self.address = camera_data.address 
            self.place = camera_data.place 
            self.camera_type = camera_data.camera_type
            self.camera_name = camera_data.camera_name 
            self.settings = camera_data.settings 
            self.phone_number = camera_data.phone_number
        
        
    def delete_camera(self, camera_id):
        self.cameras_collection.delete_one({'_id' : ObjectId(camera_id)})      
    
    def get_cameras_by_user(self,email):
       return list(self.cameras_collection.find({'user_id': email}))
   
    def get_camera_data(self, camera_id):
       return self.cameras_collection.find_one({'_id': ObjectId(camera_id)},{'user_id': 0})

    def insert_camera(self):
        self.cameras_collection.insert_one({
            'user_id': self.id,
            'ip': self.ip,
            'address': self.address,
            'place': self.place,
            'cameraType': self.camera_type,
            'cameraName': self.camera_name,
            'phoneNumber': self.phone_number,
            'settings': {
                'fires': bool(self.settings.get('fires')),
                'bladedWeapon': bool(self.settings.get('bladed_weapons')),
                'stabbing': bool(self.settings.get('stabbing')),
                "handgun" : bool(self.settings.get("handgun")),
            "longGun" : bool(self.settings.get("long_gun")),
            "brandishing" : bool(self.settings.get("brandishing")),
            "dogAggresion" : bool(self.settings.get("dog_aggression")),
            "carAccident" : bool(self.settings.get("car_accident")),
            "brawls" : bool(self.settings.get("brawls")),
            "injuredPeople" : bool(self.settings.get("injured_people"))
            }
        })
        
    def get_cameras(self):
        cameras = self.cameras_collection.find()
        cameras_data = []
        for camera in cameras:
            cameras_data.append(camera)
        return cameras_data

        