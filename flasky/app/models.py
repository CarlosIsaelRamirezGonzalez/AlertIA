"""Documentos de MongoDB: usuarios, cámaras, notificaciones y reportes."""

from datetime import datetime
import hashlib

from bson import ObjectId
from flask import current_app, flash, session
from flask_login import UserMixin, current_user
from itsdangerous import URLSafeSerializer as Serializer
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager
from .schemas import PlaceAlerts

TOKEN_LENGTH = 10


@login_manager.user_loader
def load_user(user_id):
    """Recupera al usuario de la sesión.

    Args:
        user_id: Identificador guardado en la sesión.

    Returns:
        El usuario, o None si ya no existe.
    """
    return User.objects(id=ObjectId(user_id)).first()


class User(UserMixin, db.Document):
    """Cuenta de AlertAI.

    Attributes:
        username: Nombre visible.
        email: Correo; es único y sirve para iniciar sesión.
        password_hash: Contraseña cifrada; la contraseña nunca se guarda.
        available: No se usa en el código.
        confirmed: Si ya confirmó su correo.
    """

    username = db.StringField(required=True)
    email = db.StringField(required=True, unique=True)
    password_hash = db.StringField(required=True)
    available = db.BooleanField(default=True)
    confirmed = db.BooleanField(default=False)

    def __init__(self, **kwargs):
        """Crea el usuario; el administrador queda confirmado desde el inicio.

        Args:
            **kwargs: Campos del documento.
        """
        super().__init__(**kwargs)
        if self.email == current_app.config['FLASKY_ADMIN']:
            self.confirmed = True

    @property
    def password(self):
        """La contraseña no se puede leer.

        Raises:
            AttributeError: Siempre.
        """
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Guarda la contraseña cifrada.

        Args:
            password: Contraseña en texto.
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Revisa una contraseña.

        Args:
            password: Contraseña en texto.

        Returns:
            Si es la correcta.
        """
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        """Genera el código de 10 caracteres que se manda por correo.

        Returns:
            El código en mayúsculas.
        """
        data_token = f'{self.email}{self.password_hash}{self.username}'.encode('utf-8')
        return hashlib.sha256(data_token).hexdigest()[:TOKEN_LENGTH].upper()

    def confirm_token(self, token):
        """Valida un código firmado y, si es correcto y no ha vencido, confirma la cuenta.

        El vencimiento se guarda en la sesión al enviar el código.

        Args:
            token: Código firmado con `SECRET_KEY`.

        Returns:
            Si el código fue válido.
        """
        serializer = Serializer(current_app.config['SECRET_KEY'])
        try:
            code = serializer.loads(token)
        except Exception:
            return False

        expiration_time = session.get(code) if isinstance(code, str) else None
        if not expiration_time:
            flash('The token is incorrect')
            return False
        if datetime.now() >= expiration_time:
            flash('The token has expired.')
            return False

        self.confirmed = True
        self.save()
        return True

    def reset_password(self, new_password):
        """Cambia la contraseña.

        Args:
            new_password: Contraseña nueva en texto.
        """
        self.password = new_password
        self.save()

    def __repr__(self):
        """Representación para depurar."""
        return '<User %r>' % self.username


class Notification(db.Document):
    """Amenaza detectada por una cámara.

    Attributes:
        user: Correo del dueño, como texto (ver docs/problemas-conocidos.md).
        date_time: Cuándo se detectó.
        place: Dirección de la cámara.
        threat: Amenaza, como "Incendios".
        camera_name: Nombre de la cámara.
        certainty: Certeza del modelo, como "97.31%".
        image: Foto en PNG.
        read: Si ya se abrió.
        starred: Si está destacada; las destacadas no se borran solas.
    """

    user = db.StringField(required=True)
    date_time = db.DateTimeField(required=True)
    place = db.StringField(required=True)
    threat = db.StringField(required=True)
    camera_name = db.StringField(required=True)
    certainty = db.StringField(required=True)
    image = db.BinaryField(required=True)
    read = db.BooleanField(default=False)
    starred = db.BooleanField(default=False)


class Alerts:
    """Alertas que se pueden activar en una cámara."""

    FIRES = "fires"
    BLADED_WEAPON = "bladed_weapon"
    STABBING = "stabbing"
    HANDGUN = "handgun"
    LONG_GUN = "long_gun"
    CANNONING = "cannoning"
    DOG_ATTACK = "dog_attack"
    CAR_ACCIDENT = "car_accident"
    BRAWLS = "brawls"
    INJURED_PEOPLE = "injured_people"

    @classmethod
    def all_alerts(cls):
        """Lista todas las alertas.

        Returns:
            Las alertas, en el orden de los formularios.
        """
        return [
            cls.FIRES, cls.BLADED_WEAPON, cls.STABBING, cls.HANDGUN,
            cls.LONG_GUN, cls.CANNONING, cls.DOG_ATTACK,
            cls.CAR_ACCIDENT, cls.BRAWLS, cls.INJURED_PEOPLE
        ]


# Alertas que se activan solas según el lugar. "Personalized" no está: ahí se eligen una por una.
PLACE_ALERTS = (
    PlaceAlerts(place="Home", alerts=(Alerts.FIRES, Alerts.BLADED_WEAPON, Alerts.STABBING,
                                      Alerts.HANDGUN, Alerts.DOG_ATTACK)),
    PlaceAlerts(place="Building", alerts=(Alerts.FIRES, Alerts.BLADED_WEAPON, Alerts.HANDGUN,
                                          Alerts.LONG_GUN, Alerts.CAR_ACCIDENT)),
    PlaceAlerts(place="Square", alerts=(Alerts.FIRES, Alerts.BLADED_WEAPON, Alerts.HANDGUN,
                                        Alerts.LONG_GUN, Alerts.DOG_ATTACK, Alerts.BRAWLS)),
    PlaceAlerts(place="Street", alerts=(Alerts.FIRES, Alerts.BLADED_WEAPON, Alerts.STABBING,
                                        Alerts.HANDGUN, Alerts.LONG_GUN, Alerts.CANNONING,
                                        Alerts.DOG_ATTACK, Alerts.CAR_ACCIDENT, Alerts.BRAWLS)),
)


class Camera(db.Document):
    """Cámara de un usuario y las alertas que vigila.

    Attributes:
        name: Nombre que le dio el usuario.
        phone_number: Teléfono de 10 dígitos para los SMS.
        camera_type: `WebCamera` o `SecurityCamera`.
        url: Dirección de la cámara de seguridad.
        place: Lugar: `Home`, `Building`, `Square`, `Street` o `Personalized`.
        place_default: Lugar con el que se registró.
        address: Dirección física.
        latitude: Latitud, como texto.
        longitude: Longitud, como texto.
        device_id: Cámara elegida en esta computadora.
        registered: Nombre de la computadora donde se registró; solo ahí se vigila.
        user: Dueño; si se borra el usuario, se borran sus cámaras.
        alerts: Alertas activas.
        alerts_default: Alertas con las que se registró.
    """

    name = db.StringField(required=True)
    phone_number = db.StringField(required=True)
    camera_type = db.StringField(required=True)
    url = db.StringField()
    place = db.StringField(required=True, choices=["Home", "Building", "Square", "Street", "Personalized"])
    place_default = db.StringField(required=True)
    address = db.StringField(required=True)
    latitude = db.StringField()
    longitude = db.StringField()
    device_id = db.StringField()
    registered = db.StringField()

    user = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    alerts = db.ListField(db.StringField(), required=True)
    alerts_default = db.ListField(db.StringField(), required=True)

    def __init__(self, **kwargs):
        """Crea la cámara; si no se indica el dueño, es el usuario de la sesión.

        Args:
            **kwargs: Campos del documento.
        """
        super().__init__(**kwargs)
        if self.user is None:
            self.user = current_user.id

    def __repr__(self):
        """Representación para depurar."""
        return '<Camera %r>' % self.name

    def insert_personalized_alerts(self, form):
        """Activa las alertas marcadas en el formulario.

        Args:
            form: Formulario con una casilla por alerta.
        """
        self.alerts = [alert for alert in Alerts.all_alerts() if getattr(form, alert).data]

    def insert_place_alerts(self, place):
        """Activa las alertas que corresponden a un lugar.

        Args:
            place: Lugar, como `Home`.
        """
        self.alerts = next((list(item.alerts) for item in PLACE_ALERTS if item.place == place), [])

    def has_alert(self, alert):
        """Revisa si una alerta está activa.

        Args:
            alert: Alerta, como `fires`.

        Returns:
            Si está activa.
        """
        return alert in self.alerts

    def add_alert(self, alert):
        """Activa una alerta, si no lo estaba.

        Args:
            alert: Alerta, como `fires`.
        """
        if not self.has_alert(alert):
            self.alerts.append(alert)

    def remove_alert(self, alert):
        """Desactiva una alerta, si estaba activa.

        Args:
            alert: Alerta, como `fires`.
        """
        if self.has_alert(alert):
            self.alerts.remove(alert)

    def reset_alerts(self):
        """Desactiva todas las alertas."""
        self.alerts = []

    def get_alerts(self):
        """Lista las alertas activas.

        Returns:
            Las alertas.
        """
        return self.alerts


class Report(db.Document):
    """Notificación que un usuario marcó como error, para que el administrador la revise.

    Attributes:
        title: Título del reporte.
        body: Descripción.
        label: Amenaza que se había detectado.
        date_time: Cuándo se reportó.
        user: Quien reportó.
        camera: Cámara de la notificación.
        image: Foto de la notificación.
    """

    title = db.StringField()
    body = db.StringField()
    label = db.StringField(required=True)
    date_time = db.DateTimeField(required=True)
    user = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
    camera = db.ReferenceField(Camera, reverse_delete_rule=db.CASCADE)
    image = db.BinaryField(required=True)
