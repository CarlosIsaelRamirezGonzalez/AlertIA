from pymongo import MongoClient


MONGO_URI = "mongodb+srv://enriquerc260:erJvAyN1zF9guAkV@alertai.2fssau2.mongodb.net/" 

# mongodb://root:root123@localhost:27017/?authMechanism=DEFAULT&tls=false

def get_db_connection():
    """ Obtiene una conexion a la base de datos de MongoDB
    
    Esta funcion crea y devuelve una conexion a la base de datos AlertIA, funciona como 
    administrador de contexto ya que la conexion con la base de datos se cierra cuando se llame
    y se cerrará automaticamente al finalizar
    
    Returns:
        pymongo.database.Database: Es una instancia de la base de datos de mongodb 
    """
    
    client = MongoClient(MONGO_URI)
    return client['AlertIA']

def get_cameras_by_user(email):
    db = get_db_connection()
    cameras_collection = db['cameras']
    return list(cameras_collection.find({'user_id' : email}, {'_id' : 1, 'place' : 1}))

def insert_user(user_data):
    """ Inserta un usuario en la base de datos AlertIA

    Esta función toma los datos del usuario como argumento y posteriormente los inserta en el 
    documento 'Users' de la base de datos.
    
    Args:
        user_data (UserData): Un objeto UserData que contiene la informacion del usuario
        que se compone de: username, password y email.
    """
    
    db = get_db_connection()
    user_collection = db['users']
    user_collection.insert_one({
        'username': user_data.username,
        'password': user_data.password,
        'email': user_data.email
    })

def update_password(email, password):
    """Retablece una nueva contraseña al usuario
    
    Esta funcion toma los datos email y password del usuario como argumento para 
    posteriormente actualizar el documento 'Users', actualiza solo la contraseña del email
    pasado como argumento 

    Args:
        email (string): Es el email del usuario que desea restablecer una nueva contraseña  
        password (string): Es la contraseña del usuario para acceder al sistema
    """
    
    db = get_db_connection()
    user_collection = db['users']
    user_collection.update_one({'email' : email}, {'$set': {'password': password} })
    
def insert_camera(camera_data):
    db = get_db_connection()
    cameras_collection = db['cameras']
    cameras_collection.insert_one({
        "user_id" : camera_data.user_id,
        "ip" : camera_data.ip,
        "address": camera_data.address,
        "place" : camera_data.place,
        "cameraType" : camera_data.camera_type,
        "cameraName" : camera_data.camera_name,
        "phoneNumber" : camera_data.phone_number,
        "settings" :  {
            "fires" : camera_data.settings["fires"], 
            "bladedWeapon": camera_data.settings["bladed_weapons"],
            "stabbing" : camera_data.settings["stabbing"],
            "handgun" : camera_data.settings["handgun"],
            "longGun" : camera_data.settings["long_gun"],
            "brandishing" : camera_data.settings["brandishing"],
            "dogAggresion" : camera_data.settings["dog_aggression"],
            "carAccident" : camera_data.settings["car_accident"],
            "brawls" : camera_data.settings["brawls"],
            "injuredPeople" : camera_data.settings["injured_people"]
        }
         
    })

def get_username(email):
    """Obtiene el nombre de usuario
    
    Esta funcion encuentra el nombre de usuario con base al email pasado como argumento.
    
    Args:
        email (string): Es el email del usuario del cual se desea saber el username

    Returns:
        Dict or None: Un diccionario que contiene el nombre de usuario del usuario, sin embargo 
        si dicho email no existe en la base de datos retornara un None
    """
    
    db = get_db_connection()
    user_collection = db['Users']
    return user_collection.find_one({'email': email}, {'_id': 0, 'password': 0, 'email': 0})

def existing_email(email):
    """Revisa que exista un email en el documeto 'Users' de la base de datos AlertIA
    
    Args:
        email (string): Es el email que se desea encontrar

    Returns:
        Dict or None: Si el email existe en la base de datos regresa un Diccionario con los 
        datos del usuario, si no existe regresara un None
    """
    
    db = get_db_connection()
    user_collection = db['users']
    return user_collection.find_one({'email': email})

def get_pasword(email):
    """Obtiene el password de el email pasado como argumento

    Args:
        email (String): Es el email del usuario del cual desea obtener la contraseña    

    Returns:
        Dict or None: Regresa el password en hash del usuario dueño del email.
    """
    
    db = get_db_connection()
    user_collection = db['users']
    return user_collection.find_one({'email': email},{'_id': 0, 'email': 0, 'username': 0})

def check_admin(email):
    db = get_db_connection()
    user_collection = db['users']
    data = user_collection.find_one({'email': email})

    if data is not None and data.get('admin', False):
        return True
    else:
        return False 

def get_cameras():
    db = get_db_connection()
    camara_collection = db['cameras']

    all_camaras = camara_collection.find()
    cameras_data = []

    for camera in all_camaras:
        cameras_data.append(camera)

    return cameras_data