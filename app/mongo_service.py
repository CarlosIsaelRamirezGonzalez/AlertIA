from pymongo import MongoClient
from bson import ObjectId

mongo_client = MongoClient('mongodb://root:root123@localhost:27017/?authMechanism=DEFAULT&tls=false')
mongo_database = mongo_client['AlertIA']
user_collection = mongo_database['Users']
# client.close()
def insert_user(user_data):
    user_collection.insert_one({
        'username': user_data.username,
        'password': user_data.password,
        'email': user_data.email
    })

def get_username(email):
    return user_collection.find_one({'email': email}, {'_id': 0, 'password': 0, 'email': 0})

def existing_email(email):
    return user_collection.find_one({'email': email})

def get_pasword(email):
    return user_collection.find_one({'email': email},{'_id': 0, 'email': 0, 'username': 0})
