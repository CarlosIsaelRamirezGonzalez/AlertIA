from flask_login import UserMixin
from .mongo_service import existing_email

class UserData():
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

class UserModel(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.username
        self.password = user_data.password
        self.email = user_data.email
    
    @staticmethod
    def query(email):
        user_doc = existing_email(email)
        if user_doc is not None:
            user_data = UserData(username=user_doc['username'], password=user_doc['password'], email=user_doc['email'])
            return UserModel(user_data)