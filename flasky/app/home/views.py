"""Vistas de cámaras y el monitoreo con la IA: cada cámara se vigila en su propio hilo."""

from flask import render_template, flash, url_for, redirect, current_app, request, abort
from flask_login import login_required, current_user
from ..decorators import csrf_post
from ..models import Camera, Notification, Report, User
from ..detection import ALERT_MODE_SECONDS, REPEAT_MINUTES, confirmed_threat, is_detection
from .forms import AddCameraForm, EditCameraForm, ReportNotification
from . import home
import numpy as np
import threading
from queue import Queue
import cv2
import time
import platform
from twilio.rest import Client
import os
from ..email import send_email
from ..schemas import CameraDevice, EmailAttachment, MonitoredCamera

from datetime import datetime
from PIL import Image
import io

from colorama import Fore

MODEL_INPUT_SIZE = (256, 256)
MAX_REPORTS = 25
MAX_UNSTARRED_NOTIFICATIONS = 500

notification_queue = Queue()
# Cámaras que se están vigilando en esta computadora, con su hilo.
monitored_cameras: list[MonitoredCamera] = []

# El modelo pesa varios MB y tarda en cargar: se carga una sola vez y se comparte entre cámaras.
_model = None
_model_lock = threading.Lock()
_notifications_thread_started = False


def get_model(app):
    """Carga el modelo la primera vez y después regresa el mismo.

    Args:
        app: Aplicación de Flask; de ahí sale la ruta del modelo.

    Returns:
        El modelo de Keras.
    """
    global _model
    with _model_lock:
        if _model is None:
            from tensorflow.keras.models import load_model
            _model = load_model(app.config['MODEL_PATH'])
        return _model


def start_notifications_monitor():
    """Inicia, una sola vez, el hilo que muestra los avisos de las cámaras en la consola."""
    global _notifications_thread_started
    with _model_lock:
        if _notifications_thread_started:
            return
        _notifications_thread_started = True
    threading.Thread(target=monitor_notifications, daemon=True).start()


def now_text():
    """Da la fecha y hora actuales como se muestran en los correos.

    Returns:
        El texto, como `07-11-2026 15:21`.
    """
    return datetime.now().strftime("%d-%m-%Y %H:%M")


@home.route('/home')
@login_required
def index():
    """Muestra las cámaras del usuario y empieza a vigilar las que no se estén vigilando.

    Returns:
        La página.
    """
    cameras = Camera.objects(user=current_user.id).all()
    app = current_app._get_current_object()
    model = get_model(app)
    start_notifications_monitor()

    # Se vigila cada cámara que no tenga un hilo vivo; las que fallaron se vuelven a intentar.
    for camera in cameras:
        current = next((item for item in monitored_cameras if item.camera_id == str(camera.id)), None)
        if current is not None and current.thread.is_alive():
            continue
        if current is not None:
            monitored_cameras.remove(current)
        thread = threading.Thread(target=start_camera_monitoring, args=[app, camera, model, current_user.email], daemon=True)
        thread.start()
        monitored_cameras.append(MonitoredCamera(camera_id=str(camera.id), thread=thread))

    return render_template('home/home.html', cameras=cameras)


@home.route('/reportNotification/<id_notification>', methods=['GET', 'POST'])
@login_required
def report_notification(id_notification):
    """Reporta una notificación del usuario como errónea, para que la revise el administrador.

    Args:
        id_notification: Identificador de la notificación.

    Returns:
        El formulario, o una redirección a las notificaciones.
    """
    form = ReportNotification()
    notification = Notification.objects(id=id_notification, user=current_user.email).first()
    if not notification:
        flash("That notification doesn't exists")
        return redirect(url_for('home.index'))
    camera = Camera.objects(user=current_user.id, name=notification.camera_name).first()

    if form.validate_on_submit():
        if Report.objects.count() >= MAX_REPORTS:
            oldest_report = Report.objects.order_by('date_time').first()
            if oldest_report:
                oldest_report.delete()
        report = Report(title=form.title.data,
                        body=form.description.data,
                        date_time=datetime.now(),
                        label=notification.threat,
                        user=current_user._get_current_object(),
                        camera=camera,
                        image=notification.image)
        report.save()
        flash("Report done successfully")
        return redirect(url_for('alert.notifications'))

    return render_template('home/report_notification.html', form=form)


@home.route('/addCamera', methods=['GET', 'POST'])
@login_required
def add_camera():
    """Registra una cámara con sus alertas, según el lugar o una por una.

    Returns:
        El formulario, o una redirección a las cámaras.
    """
    form = AddCameraForm()
    camera_details = get_camera_details()
    form.device_id.choices = [(device.device_id, device.name) for device in camera_details]

    if form.validate_on_submit():
        camera = Camera(
            name=form.name.data,
            phone_number=form.phone_number.data,
            camera_type=form.camera_type.data,
            url=form.url.data,
            place=form.place.data,
            address=form.address.data,
            latitude=str(form.latitude.data),
            longitude=str(form.longitude.data),
            device_id=form.device_id.data,
            registered=platform.node()
        )

        if form.place.data != 'Personalized':
            camera.insert_place_alerts(form.place.data)
        else:
            camera.insert_personalized_alerts(form)

        camera.alerts_default = camera.alerts.copy()
        camera.place_default = camera.place

        if not camera.alerts:
            flash('Error: You must select at least one place or alert.')
        else:
            camera.save()
            flash("Camera saved successfully")
            return redirect(url_for('home.index'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'error')

    return render_template('home/add-camera.html', form=form)


def get_camera_details() -> list[CameraDevice]:
    """Lista las cámaras conectadas a esta computadora.

    En Windows agrega los nombres de las cámaras USB con WMI; en cualquier sistema prueba los
    índices de OpenCV hasta que uno no responda.

    Returns:
        Las cámaras encontradas.
    """
    devices: list[CameraDevice] = []

    # Windows: nombres de las cámaras USB.
    if platform.system() == "Windows":
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\cimv2")
        for item in service.ExecQuery("Select * from Win32_PnPEntity where Description like '%USB Video Device%'"):
            devices.append(CameraDevice(device_id=item.DeviceID, name=item.Name))

    # Cualquier sistema: cámaras por número, hasta que una no responda.
    index = 0
    while True:
        cap = cv2.VideoCapture(index)
        ok = cap.read()[0]
        cap.release()
        if not ok:
            break
        if not any(device.device_id == str(index) for device in devices):
            name = f"Camera {index} (Integrated)" if index == 0 else f"Camera {index}"
            devices.append(CameraDevice(device_id=str(index), name=name))
        index += 1
    return devices


def get_own_camera(camera_id):
    """Busca una cámara del usuario de la sesión.

    Args:
        camera_id: Identificador de la cámara.

    Returns:
        La cámara.

    Raises:
        NotFound: Si no existe o es de otra persona (responde 404).
    """
    camera = Camera.objects(id=camera_id, user=current_user.id).first()
    if not camera:
        abort(404)
    return camera


@home.route('/editCamera/<camera_id>', methods=['GET', 'POST'])
@login_required
def edit_camera(camera_id):
    """Cambia una cámara del usuario, o regresa sus alertas a las originales.

    Args:
        camera_id: Identificador de la cámara.

    Returns:
        El formulario, o una redirección a las cámaras.
    """
    camera = get_own_camera(camera_id)
    form = EditCameraForm(obj=camera)

    # Marca en el formulario las alertas que ya tiene la cámara personalizada.
    if request.method == 'GET' and camera.place == "Personalized":
        for alert in camera.get_alerts():
            if hasattr(form, alert):
                getattr(form, alert).data = True

    if form.validate_on_submit():
        submit_type = request.form.get('submit_type')
        camera.name = form.name.data
        camera.phone_number = form.phone_number.data
        camera.place = form.place.data
        camera.address = form.address.data
        if submit_type == 'update_default':
            camera.alerts = camera.alerts_default.copy()
            camera.place = camera.place_default
        elif form.place.data != 'Personalized':
            camera.insert_place_alerts(form.place.data)
        else:
            camera.insert_personalized_alerts(form)

        if not camera.alerts:
            flash('Error: You must select at least one place or alert.')
        else:
            camera.save()
            flash("Camera updated successfully")
            return redirect(url_for('home.index'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'error')

    return render_template('home/edit-camera.html', form=form, camera=camera)


@home.route('/deleteCamera/<camera_id>', methods=['POST'])
@login_required
@csrf_post
def delete_camera(camera_id):
    """Borra una cámara del usuario.

    Args:
        camera_id: Identificador de la cámara.

    Returns:
        Una redirección a las cámaras.
    """
    get_own_camera(camera_id).delete()
    flash('Camera deleted successfully', 'success')
    return redirect(url_for('home.index'))


def start_camera_monitoring(app, camera, model, user_email):
    """Vigila una cámara hasta que se desconecte: clasifica cada cuadro y avisa de las amenazas.

    Corre en su propio hilo. Si la cámara se registró en otra computadora, no hace nada.

    Args:
        app: Aplicación de Flask, para la base de datos y el correo.
        camera: Cámara que se vigila.
        model: Modelo de Keras ya cargado.
        user_email: Correo del dueño.
    """
    with app.app_context():
        detections = []
        alert_mode_time = time.time()
        alert_mode = False

        def connect_camera():
            """Abre la cámara de seguridad por su URL, o la webcam elegida.

            Returns:
                La captura de OpenCV, o None si no se pudo abrir.
            """
            if camera.camera_type == "SecurityCamera":
                cap = cv2.VideoCapture(camera.url)
            else:
                # Usa la cámara que se eligió al registrarla; antes siempre se abría la 0.
                index = int(camera.device_id) if (camera.device_id or "").isdigit() else 0
                cap = cv2.VideoCapture(index)

            if not cap.isOpened():
                notification_queue.put(f"Failed to connect to camera {camera.name}")
                return None
            return cap

        def process_frame(cap):
            """Clasifica un cuadro y, si se confirma una amenaza, la notifica.

            Args:
                cap: Captura de OpenCV.

            Returns:
                Si se pudo leer el cuadro.
            """
            nonlocal alert_mode, alert_mode_time
            ret, frame = cap.read()
            if not ret:
                return False

            # OpenCV entrega BGR; el modelo se entrenó con imágenes RGB.
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_array = cv2.resize(rgb_frame, MODEL_INPUT_SIZE).astype("float32") / 255.0
            predictions = model.predict(np.expand_dims(image_array, axis=0), verbose=0)
            predicted_class = int(np.argmax(predictions, axis=1)[0])
            certainty = float(predictions[0][predicted_class])

            if is_detection(predicted_class, certainty):
                detections.append(predicted_class)
                alert_mode = True
                alert_mode_time = time.time()
                threat = confirmed_threat(detections, camera.alerts)
                if threat:
                    create_notification(rgb_frame, threat, f"{certainty * 100:.2f}%")
            elif (time.time() - alert_mode_time) > ALERT_MODE_SECONDS:
                alert_mode = False
                detections.clear()
            return True

        def create_notification(rgb_frame, threat, certainty):
            """Guarda la notificación con la foto y avisa por correo, sin repetir la misma amenaza seguido.

            Args:
                rgb_frame: Cuadro de la cámara en RGB.
                threat: Amenaza confirmada.
                certainty: Certeza, como "97.31%".
            """
            last_notification = Notification.objects(user=user_email, threat=threat).order_by('-date_time').first()
            if last_notification and isinstance(last_notification.date_time, datetime):
                if (datetime.now() - last_notification.date_time).total_seconds() / 60 <= REPEAT_MINUTES:
                    return

            output = io.BytesIO()
            Image.fromarray(rgb_frame).save(output, format='PNG')
            image_data = output.getvalue()

            notification = Notification(
                user=user_email,
                date_time=datetime.now(),
                place=camera.address,
                threat=threat,
                camera_name=camera.name,
                certainty=certainty,
                image=image_data
            )
            notification.save()

            info_user = User.objects.get(email=user_email)
            attachments = [EmailAttachment(filename='alert_image.png', content_type='image/png', data=image_data)]
            send_email(user_email,
                       'Damage detected',
                       "alert/email/alert",
                       user=info_user,
                       alert=threat,
                       camera_name=camera.name,
                       certainty=certainty,
                       time=now_text(),
                       link=f"{app.config['BASE_URL']}/alert/notifications/view/{notification.id}",
                       attachments=attachments)

            unstarred = Notification.objects(user=user_email, starred=False)
            if unstarred.count() > MAX_UNSTARRED_NOTIFICATIONS:
                unstarred.order_by('date_time').first().delete()

        def notify_disconnected():
            """Avisa por correo que la cámara se desconectó."""
            info_user = User.objects.get(email=user_email)
            send_email(user_email,
                       'Camera disconected',
                       'alert/email/camera_disconected',
                       user=info_user,
                       camera_name=camera.name,
                       time=now_text())

        try:
            if camera.registered != platform.node():
                print(f"{camera.name} no fue registrada en {platform.node()}")
                return
            cap = connect_camera()
            if cap is None:
                return


            while cap.isOpened():
                if not process_frame(cap):
                    notification_queue.put(f'Camera {camera.name} disconnected, attempting to reconnect...')
                    time.sleep(.5)
                    cap.release()
                    cap = connect_camera()
                    if cap is None or not process_frame(cap):
                        notify_disconnected()
                        notification_queue.put(f'Camera {camera.name} disconnected')
                        break
                if not alert_mode:
                    time.sleep(1)

            if cap is not None:
                cap.release()
        except Exception as e:
            print(Fore.RED, f"Exception in start_camera_monitoring for camera {camera.name}: {e}")
            notify_disconnected()


def monitor_notifications():
    """Muestra en la consola los avisos de las cámaras; corre en su propio hilo."""
    while True:
        if not notification_queue.empty():
            print(notification_queue.get())
        time.sleep(1)


def send_alert_message_sms(camera, threat):
    """Envía un SMS con Twilio. Está desactivado: no se llama desde ningún lado.

    Args:
        camera: Cámara que detectó la amenaza; su teléfono recibe el mensaje.
        threat: Amenaza detectada.
    """
    client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
    body_message = f"AlertAI detecto: {threat} en la camara {camera.name} ubicada en {camera.address}"[:160]
    message = client.messages.create(
        from_=os.environ.get('TWILIO_FROM_NUMBER'),
        to=f"+52{camera.phone_number}",
        body=body_message
    )
    print(message.sid)
