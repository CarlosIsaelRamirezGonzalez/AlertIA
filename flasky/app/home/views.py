from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model

from flask import render_template, flash, url_for, redirect, current_app, request
from flask_login import login_required, current_user
from ..decorators import post_only
from ..models import Camera, Notification, Report, User, Alerts
from .forms import AddCameraForm, EditCameraForm, ReportNotification
from . import home
import numpy as np
import threading
from queue import Queue
import cv2
import time
import pythoncom
import win32com.client
import platform
from twilio.rest import Client
import os
from ..email import send_email


from datetime import datetime
from PIL import Image
import io

from colorama import Fore


notification_queue = Queue()
active_cameras = {}
monitoring_threads = {}

@home.route('/home')
@login_required
def index():
    
    cameras = Camera.objects(user=current_user.id).all()
    
    modelo_ruta = 'C:/Users/Carlos Ramirez/Desktop/Programas/AlertIA/Artificial_Intelligence/Aria.keras'
    modelo = load_model(modelo_ruta)
    
    monitoring_thread = threading.Thread(target=monitor_notifications, daemon=True)
    monitoring_thread.start()
    
    app = current_app._get_current_object()
    threads_monitoring_cameras = list()
    for camera in cameras:
        if camera.name not in monitoring_threads:
            t = threading.Thread(target=start_camera_monitoring, args=[app, camera, modelo, current_user.email], daemon=True)
            threads_monitoring_cameras.append(t)
            t.start()
            monitoring_threads[camera.name] = t
        

    
    
    return render_template('home/home.html', cameras=cameras)

@home.route('/reportNotification/<id_notification>', methods=['GET', 'POST'])
@login_required
def report_notification(id_notification):
    form = ReportNotification()
    notification = Notification.objects(id=id_notification).first()
    camera = Camera.objects(name=notification.camera_name).first()
    if not notification:
        flash("That notification doesn't exists")
        return redirect(url_for('home.index'))
    
    if form.validate_on_submit():
        reports_quantity = Report.objects.count() 
        if reports_quantity >= 25:
            oldest_report = Report.objects.order_by('date_time').first()
            if oldest_report:
                oldest_report.delete()
        report = Report(title=form.title.data,
                        body=form.description.data,
                        date_time=datetime.now(),
                        label = notification.threat,
                        user = current_user.username,
                        camera = camera,
                        image = notification.image)
                    

        report.save()
        flash("Report done successfully")
        return redirect(url_for('alert.notifications'))

    
    return render_template('home/report_notification.html', form=form)

    

@home.route('/addCamera', methods=['GET', 'POST'])
@login_required
def add_camera():
    form = AddCameraForm()
    
    camera_details = get_camera_details()
    form.device_id.choices = [(cam["DeviceID"], cam["Name"]) for cam in camera_details]
    
    print(camera_details)
    
    if form.validate_on_submit():
        
        # Borraste a que usuario se conectaba???
        camera = Camera(
            name = form.name.data, 
            phone_number = form.phone_number.data,
            camera_type = form.camera_type.data, 
            url = form.url.data, 
            place = form.place.data,
            address = form.address.data, 
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            device_id = form.device_id.data, 
            registered = platform.node())
        
        
        if form.place.data != 'Personalized':
            camera.insert_place_alerts(form.place.data)
        else:
            camera.insert_personalized_alerts(form)
        camera.place_default = camera.alerts
        # save model
        if camera.alerts == 0:
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

def get_camera_details():
    pythoncom.CoInitialize()
    str_name = "root\\cimv2"
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    obj_swm = wmi.ConnectServer(".", str_name)
    col_items = obj_swm.ExecQuery("Select * from Win32_PnPEntity where Description like '%USB Video Device%'")
    camera_details = []
    for item in col_items:
        camera_details.append({
            "DeviceID": item.DeviceID,
            "Name": item.Name
        })
        
    index = 0
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        # Verificar si ya está en la lista de cámaras USB
        if not any(cam['DeviceID'] == str(index) for cam in camera_details):
            camera_details.append({
                "DeviceID": str(index),
                "Name": f"Camera {index} (Integrated)" if index == 0 else f"Camera {index}"
            })
        cap.release()
        index += 1
    return camera_details

@home.route('/editCamera/<camera_id>', methods=['GET', 'POST'])
@login_required
def edit_camera(camera_id):
    print("ENTRE")
    print("/n/n/n/n/n \n \n \n \n ")
    camera = Camera.objects(id=camera_id).first()
    if not camera:
        flash("Camera not found")
        return redirect(url_for('home.index'))
    
    form = EditCameraForm(obj=camera)
    if camera.place == "Personalized":
        alerts = camera.get_alerts
        print(alerts)
    
    if form.validate_on_submit():
        submit_type = request.form.get('submit_type')
        camera.name = form.name.data
        camera.phone_number = form.phone_number.data
        camera.place = form.place.data
        camera.address = form.address.data
        print("ENTRE")
        print(form.place.data)
        if submit_type == 'update_default':
            camera.alerts = camera.place_default
        else:
            if form.place.data != 'Personalized':
                camera.insert_place_alerts(form.place.data)
            else:
                camera.insert_personalized_alerts(form)
        
        # save model
        if camera.alerts == 0:
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

@home.route('/deleteCamera/<camera_id>', methods=['GET', 'POST'])
@login_required
#@post_only
def delete_camera(camera_id):
    camera = Camera.objects(id=camera_id).first()
    camera.delete()
    flash('Camera deleted successfully', 'success')
    return redirect(url_for('home.index'))

        
    
def start_camera_monitoring(app, camera, modelo, user_email):
    with app.app_context():
        arr_check_damage = []
        alert_mode_time = time.time()
        alert_mode = False
        
        def connect_camera():
            if camera.camera_type == "SecurityCamera":
                cap = cv2.VideoCapture(camera.url)
            else:
                cap = cv2.VideoCapture(0)
                
            if not cap.isOpened():
                notification_queue.put(f"Failed to connect to camera {camera.name}")
                return None
            return cap
        
        def process_frame(cap, user_email):
            nonlocal alert_mode, alert_mode_time
            ret, frame = cap.read()
            if not ret:
                return False
            

            frame_resized = cv2.resize(frame, (256, 256))
            image_array = image.img_to_array(frame_resized)
            image_array = image_array/255.0
            image_array = np.expand_dims(image_array, axis=0)
            
            predictions = modelo.predict(image_array)
            predicted_classes = np.argmax(predictions, axis=1)
            
            certainty = predictions[0][predicted_classes[0]]
            certainty_str = f"{certainty * 100:.2f}%"
            
            if predicted_classes[0] != 11 and certainty > 0.95:
                print("Paso algo")
                arr_check_damage.append(predicted_classes[0])
                alert_mode = True
                alert_mode_time = time.time()
                check_before_notify(frame, camera, user_email, certainty_str)
            elif (time.time() - alert_mode_time) > 20: #Aqui es 20
                alert_mode = False
                arr_check_damage.clear()
            print(predicted_classes)
            print(camera.name)
            print(alert_mode)
            return True
        
        def create_notifications(frame, camera, threat, user_email, certainty):
            last_notification = Notification.objects(user = user_email, threat = threat).order_by('-date_time').first()
            if last_notification:
                if ((datetime.now() - last_notification.date_time).total_seconds())/60 <= 3:
                    print("No han pasado 3 minutos con la misma amenaza")
                    return
            image = Image.fromarray(frame)
            output = io.BytesIO()
            image.save(output, format='PNG')
            image_data_compressed = output.getvalue()
            
            print(f"Ya entre, creando notificacion de {threat}")
            print(certainty)
            
            notificacion = Notification(
                user = user_email,
                date_time = datetime.now(),
                place = camera.address,  
                threat = threat,  
                camera_name = camera.name, 
                certainty = certainty,
                image = image_data_compressed 
            )
            notificacion.save()
                     
            info_user = User.objects.get(email = user_email) 
            attachments = [
                {
                    'filename': 'alert_image.png',
                    'content_type': 'image/png',
                    'data': image_data_compressed
                }
            ]
            send_email(user_email,
                       'Damage detected',
                       "alert/email/alert",
                       user = info_user, 
                       alert = threat,
                       camera_name = camera.name,
                       certainty = certainty,
                       time = datetime.now(),
                       link = f"http://127.0.0.1:5000/alert/notifications/view/{notificacion.id}",
                       attachments=attachments)
            
            if Notification.objects(user = user_email, starred = False).count() > 500:
                Notification.objects(user=user_email, starred=False).order_by('date_time').first().delete()

            
        
            
            # send_alert_message_sms(camera, threat)
            # flash('Alerta creada correctamente', 'success')
            
        def check_before_notify(frame, camera, user_email, certainty):
            
            if arr_check_damage.count(1) + arr_check_damage.count(2) +  arr_check_damage.count(5) >= 10:
                if camera.has_alert(Alerts.HANDGUN) or camera.has_alert(Alerts.LONG_GUN) or camera.has_alert(Alerts.CANNONING):
                    create_notifications(frame, camera, "Armas de fuego", user_email, certainty)
                
            elif arr_check_damage.count(0) >= 10:
                if camera.has_alert(Alerts.BLADED_WEAPON):
                    create_notifications(frame, camera, "Armas blancas", user_email, certainty)
                
            elif arr_check_damage.count(3) >= 15:
                if camera.has_alert(Alerts.DOG_ATTACK):
                    create_notifications(frame, camera, "Ataque de perros", user_email, certainty)
                
            elif arr_check_damage.count(7) >= 20: #Aqui deben ser 20
                if camera.has_alert(Alerts.FIRES):
                    create_notifications(frame, camera, "Incendios", user_email, certainty)
                else:
                    print(Fore.LIGHTRED_EX, "No se hizo por la restriccion")
                    
            elif arr_check_damage.count(4) >= 30: #Aqui deben ser 30
                if camera.has_alert(Alerts.CAR_ACCIDENT):
                    create_notifications(frame, camera, "Choques", user_email, certainty)
                else:
                    print(Fore.GREEN, "No se hizo por la restriccion")
                    
            elif arr_check_damage.count(9) >= 30: #Tambien aqui
                if camera.has_alert(Alerts.INJURED_PEOPLE):
                    create_notifications(frame, camera, "Persona herida", user_email, certainty)
                
            elif arr_check_damage.count(6) + arr_check_damage.count(8) + arr_check_damage.count(10) >= 30:
                if camera.has_alert(Alerts.BRAWLS):
                    create_notifications(frame, camera, "Pelea", user_email, certainty)
                
            elif arr_check_damage.count(5) >= 10:
                if camera.has_alert(Alerts.CANNONING):
                    create_notifications(frame, camera, "Encañonamiento", user_email, certainty)
            

        try:
            if camera.registered != platform.node():
                print(f"{camera.name} no fue registrada en {platform.node()}")
                return
            cap = connect_camera()
            if cap is None:
                return
            
            active_cameras[camera.name] = cap

            while cap.isOpened():
                if not process_frame(cap, user_email):
                    notification_queue.put(f'Camera {camera.name} disconnected, attempting to reconnect...')
                    time.sleep(.5)  
                    cap.release()
                    cap = connect_camera()
                    active_cameras[camera.name] = cap
                    
                    if not cap.isOpened() or not process_frame(cap, user_email):
                        # Que camara se desconecto y a que hora camera.id
                        info_user = User.objects.get(email = user_email)
                        send_email(user_email,
                            'Camera disconected', 
                            'alert/email/camera_disconected',
                            user = info_user,  
                            camera_name = camera.name, 
                            time = datetime.now)
                        
                        notification_queue.put(f'Camera {camera.name} disconnected')
                        break
                if alert_mode == False:
                    time.sleep(1)
                    
            
            cap.release()
            if camera.name in active_cameras:
                del active_cameras[camera.name]
        except Exception as e:
            print(Fore.RED, f"Exception in start_camera_monitoring for camera {camera.name}: {e}")
            
def monitor_notifications():
    while True:
        if not notification_queue.empty():
            notification = notification_queue.get()
            print(notification)
        time.sleep(1)
        
def send_alert_message_sms(camera, threat):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    body_message = f"AlertAI detecto: {threat} en la camara {camera.name} ubicada en {camera.address}"
    
    if len(body_message) > 160:
        body_message = body_message[:160]
    
    message = client.messages.create(
        from_ = '+19378979119',
        to = f"+52{camera.phone_number}",
        body = body_message
    )
    
    print(message.sid)
    