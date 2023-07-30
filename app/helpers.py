from flask_mail import Message,Mail
from flask import current_app, session
import hashlib
import sys
from itsdangerous import URLSafeSerializer

def send_message(email, token, username, case="Validate email"):
    """Manda un gmail al usuario

    Args:
        email (String): Es el email del usuario que deseamos enviar un correo
        token (string): Es el token que le enviaremos al usuario en el correo
        username (String): Es el nombre de usuario relacionado con el gmail al cual
        enviaremos correo
        case (String): Es el asunto del gmail, si es para recuperar contraseña, validar correo,
        
    """
    bodies = {
        "Validate email": f"""
Hola, {username}: \n 
Tu token es: {token}. Úsalo para verificar tu correo. \n 
Te recordamos que por tu seguridad este token tiene vigencia solo durante los proximos 3 minutos. \n
Si no solicitaste esto, simplemente ignora este mensaje. \n
Saludos,
Atte: El equipo de AlertIA
        """,
        "Forgot password": f"""  
Hola, {username}: \n 
Tu token es: {token}. Úsalo para restablecer tu contraseña. \n 
Te recordamos que por tu seguridad este token tiene vigencia solo durante los proximos 3 minutos. \n
Si no solicitaste esto, simplemente ignora este mensaje. \n
Saludos,
Atte: El equipo de AlertIA
        """
    }
    BODY = bodies.get(case)
    mail = current_app.extensions.get('mail')
    with current_app.app_context():
        msg = Message(subject=f"Tu token es {token}", recipients=[email], body=BODY)
        mail.send(msg)
        
def delete_sessions(sessions_to_delete):
    """Elimina multiples sesiones a la vez

    Args:
        sessions_to_delete (list): Una lista de cadenas que representan las sesiones
    """
    
    for sessions_key in sessions_to_delete:
        if sessions_key in session:
            del session[sessions_key]
        
def generate_token(email, password, username):
    """Genera un token.
    Este token se utiliza para fines de verificación y autenticación del usuario en el sistema.
    Se crea combinando el email, la contraseña y el nombre de usuario proporcionados como entrada.
    Luego, se calcula un hash SHA-256 de la cadena combinada y se toman los primeros 5 caracteres
    como el token final.

    Args:
        email (String): Es el email del usuario.
        password (String): Es la contraseña del usuario para acceder al sistema.
        username (String): Es el nombre de usuario con el que el usuario se dio de alta
        en el sistema.

    Returns:
        str: Un token de 5 caracteres de seguridad unico generado para el usuario
    """
    
    data = f'{email}{password}{username}'.encode('utf-8')
    hash_result = hashlib.sha256(data).hexdigest()
    token = hash_result[:5]
    return token
# Token, duracion del token y que desde signup me rediriga a el inicio de sesion de la pagina