"""Envío de correos con Flask-Mail, en un hilo aparte para no hacer esperar al usuario."""

from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from . import mail
from .schemas import EmailAttachment


def send_async_email(app, msg):
    """Envía un correo dentro del contexto de la aplicación.

    Args:
        app: Aplicación de Flask.
        msg: Correo ya armado.
    """
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, attachments: list[EmailAttachment] | None = None, **kwargs):
    """Arma un correo con sus versiones de texto y HTML, y lo envía en otro hilo.

    Args:
        to: Destinatario.
        subject: Asunto, sin el prefijo de AlertAI.
        template: Plantilla sin extensión, como `auth/email/confirm`.
        attachments: Archivos adjuntos.
        **kwargs: Datos para la plantilla.

    Returns:
        El hilo que envía el correo.
    """
    app = current_app._get_current_object()
    msg = Message(subject=app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    for attachment in attachments or []:
        msg.attach(attachment.filename, attachment.content_type, attachment.data)

    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread
