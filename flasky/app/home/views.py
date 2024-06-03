from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model

from flask import render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from ..decorators import post_only
from ..models import Camera, User, Notification
from .forms import AddCameraForm, EditCameraForm
from . import home
import numpy as np
import threading
from queue import Queue
import cv2
import time
from collections import Counter

import base64
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
    
    modelo_ruta = 'D:\Respaldo\Escuela\Proyecto\AlertAI\Artificial_Intelligence\AlertAI-Deluxe.keras'
    modelo = load_model(modelo_ruta)
    
    monitoring_thread = threading.Thread(target=monitor_notifications, daemon=True)
    monitoring_thread.start()
    
    threads_monitoring_cameras = list()
    for camera in cameras:
        if camera.name not in monitoring_threads:
            t = threading.Thread(target=start_camera_monitoring, args=(camera, modelo, current_user.email), daemon=True)
            threads_monitoring_cameras.append(t)
            t.start()
            monitoring_threads[camera.name] = t
        

    
    
    return render_template('home/home.html', cameras=cameras)

@home.route('/addCamera', methods=['GET', 'POST'])
@login_required
def add_camera():
    form = AddCameraForm()
    
    if form.validate_on_submit():
        
        # Create model
        camera = Camera(name=form.name.data, phone_number=form.phone_number.data,
                        camera_type=form.camera_type.data, url=form.url.data, place=form.place.data,
                        address=form.address.data)
        
        
        if form.place.data != 'Personalized':
            camera.insert_place_alerts(form.place.data)
        else:
            camera.insert_personalized_alerts(form)
        # save model
        camera.save()
        flash("Camera saved successfully")
        return redirect(url_for('home.index'))        
     
    return render_template('home/add-camera.html', form=form)

@home.route('/editCamera/<camera_id>', methods=['GET', 'POST'])
@login_required
def edit_camera(camera_id):
    print("Si entre")
    camera = Camera.objects(id=camera_id).first()
    if not camera:
        flash("Camera not found")
        return redirect(url_for('home.index'))
    
    
    
    form = EditCameraForm(obj=camera)
    
    if form.validate_on_submit():
        camera.name = form.name.data
        camera.phone_number = form.phone_number.data
        camera.camera_type = form.camera_type.data
        camera.url = form.url.data
        camera.place = form.place.data
        camera.address = form.address.data
        
        camera.save()
        flash("Camera updated successfully")
        return redirect(url_for('home.index'))
    
    return render_template('home/add-camera.html', form=form, edit_mode=True, camera=camera)

@home.route('/deleteCamera/<camera_id>', methods=['GET', 'POST'])
@login_required
#@post_only
def delete_camera(camera_id):
    camera = Camera.objects(id=camera_id).first()
    camera.delete()
    flash('Camera deleted successfully', 'success')
    return redirect(url_for('home.index'))

        
    
def start_camera_monitoring(camera, modelo, user_email):
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
        
        #Forma comun
        frame_resized = cv2.resize(frame, (255, 255))
        image_array = image.img_to_array(frame_resized)
        imagen_preprocesada = preprocess_input(image_array)
        
        predictions = modelo.predict(np.array([imagen_preprocesada]))
        predicted_classes = np.argmax(predictions, axis=1)
        
        #Forma dada por Carlos
        '''frame_resized = cv2.resize(frame, (256, 256))
        image_array = image.img_to_array(frame_resized)
        image_array = image_array/255.0
        image_array = np.expand_dims(image_array, axis=0)
        #imagen_preprocesada = preprocess_input(image_array)
        
        predictions = modelo.predict(image_array)
        predicted_classes = np.argmax(predictions, axis=1)'''
        
        if predicted_classes[0] != 11:
            print("Paso algo")
            arr_check_damage.append(predicted_classes[0])
            alert_mode = True
            alert_mode_time = time.time()
            check_before_notify(frame, camera, user_email)
        elif (time.time() - alert_mode_time) > 5: #Aqui es 20
            alert_mode = False
            arr_check_damage.clear()
        print(predicted_classes)
        print(camera.name)
        print(alert_mode)
        return True
    
    def create_notifications(frame, camera, threat, user_email):
        last_notification = Notification.objects(user = user_email, threat = threat).order_by('-date_time').first()
        if last_notification:
            if ((datetime.now() - last_notification.date_time).total_seconds())/60 <= 3:
                print("No han pasado 3 minutos con la misma amenaza")
                return
        image = Image.fromarray(frame)
        output = io.BytesIO()
        image.save(output, format='PNG')
        image_data_compressed = output.getvalue()
        
        print("Ya entre")
        
        
        '''diccionario = {
            0: "Arma blanca",
            1: "Arma corta",
            2: "Arma larga",
            3: "Ataque de perro",
            4: "Choques",
            5: "Encañonamiento",
            6: "Forcejeos",
            7: "Incendios",
            8: "Patadas",
            9: "Personas heridas",
            10: "Golpes",
            11: "Normalidad"
        }'''
        
        
        notificacion = Notification(
            user = user_email,
            date_time = datetime.now(),
            place = camera.address,  
            threat = threat,  
            camera_name = camera.name, 
            certainty = 'Certeza por defecto',
            image = image_data_compressed 
        )
        notificacion.save()
        #flash('Alerta creada correctamente', 'success')
        
    def check_before_notify(frame, camera, user_email):
        if arr_check_damage.count(1) + arr_check_damage.count(2) +  arr_check_damage.count(5) >= 10:
            create_notifications(frame, camera, "Armas de fuego", user_email)
        elif arr_check_damage.count(0) >= 10:
            create_notifications(frame, camera, "Armas blancas", user_email)
        elif arr_check_damage.count(3) >= 15:
            create_notifications(frame, camera, "Ataque de perros", user_email)
        elif arr_check_damage.count(7) >= 5: #Aqui deben ser 20
            create_notifications(frame, camera, "Incendios", user_email)
        elif arr_check_damage.count(4) >= 30:
            create_notifications(frame, camera, "Choques", user_email)
        elif arr_check_damage.count(9) >= 5: #Tambien aqui
            create_notifications(frame, camera, "Persona herida", user_email)
        elif arr_check_damage.count(6) + arr_check_damage.count(8) + arr_check_damage.count(10) >= 30:
            create_notifications(frame, camera, "Pelea", user_email)
        elif arr_check_damage.count(5) >= 10:
            create_notifications(frame, camera, "Encañonamiento", user_email)
        

    try:
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
                    notification_queue.put(f'Camera {camera.name} disconnected')
                    break
            if alert_mode == False:
                time.sleep(3)
                
        
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
        
        
