from flask_login import UserMixin
from .mongo_service import existing_email, insert_camera


class UserData():
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

class UserModel(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.email
        self.password = user_data.password
        self.username = user_data.username
    
    @staticmethod
    def query(email):
        user_doc = existing_email(email)
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
    def __init__(self):
        pass 
    
    def __init__(self, camera_data):
        self.id = camera_data.user_id
        self.ip = camera_data.ip
        self.address = camera_data.address 
        self.place = camera_data.place 
        self.camera_type = camera_data.camera_type
        self.camera_name = camera_data.camera_name 
        self.settings = camera_data.settings 
        self.phone_number = camera_data.phone_number
        
    def insert(self, camera_model):
        insert_camera(camera_model)
    


        