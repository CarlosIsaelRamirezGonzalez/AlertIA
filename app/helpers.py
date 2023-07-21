from flask_mail import Message,Mail
from flask import current_app
import hashlib
import sys
from itsdangerous import URLSafeSerializer

def send_message(email, token):
    mail = current_app.extensions.get('mail')
    with current_app.app_context():
        msg = Message(subject="Token cuenta", recipients=[email], body=f" Tu token es: {token} ")
        mail.send(msg)
        
def generate_token(email, password='123456789', username='qwertyuiop'):
    data = f'{email}{password}{username}'.encode('utf-8')
    hash_result = hashlib.sha256(data).hexdigest()
    token = hash_result[:9]
    return token
# Token, duracion del token y que desde signup me rediriga a el inicio de sesion de la pagina