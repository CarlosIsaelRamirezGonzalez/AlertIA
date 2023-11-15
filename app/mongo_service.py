from pymongo import MongoClient

class Database: 
    def __init__(self):
        self.MONGO_URI = "mongodb://root:root123@localhost:27017/?authMechanism=DEFAULT&tls=false"
        # mongodb+srv://enriquerc260:erJvAyN1zF9guAkV@alertai.2fssau2.mongodb.net/
        self.client = MongoClient(self.MONGO_URI)
        self.db = self.client['AlertIA']    
    
    def cameras_collection(self):
        return self.db['cameras']
    
    def users_collection(self):
        return self.db['users']