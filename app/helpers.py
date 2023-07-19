from flask_mail import Message,Mail
from flask import current_app

def send_message(email):
    mail = current_app.extensions.get('mail')
    with current_app.app_context():
        msg = Message(subject="Token cuenta", recipients=email, body="Hola este es el body")
        mail.send(msg)

