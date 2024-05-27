from flask import render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from ..models import Camera
from .forms import AddCameraForm, EditCameraForm
from . import home
import numpy as np
import threading
from queue import Queue
import cv2
import time
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
from app.alert.views import create_notifications
from colorama import Fore

notification_queue = Queue()
active_cameras = {}
monitoring_threads = {}

@home.route('/home')
@login_required
def index():
    cameras = Camera.objects(user=current_user.id).all()
    
    modelo_ruta = 'D:/Respaldo/Escuela/Proyecto/AlertAI/Artificial_Intelligence/AlertAI_V2.keras'
    modelo = load_model(modelo_ruta)
    
    monitoring_thread = threading.Thread(target=monitor_notifications, daemon=True)
    monitoring_thread.start()
    
    threads_monitoring_cameras = list()
    for camera in cameras:
        if camera.name not in monitoring_threads:
            t = threading.Thread(target=start_camera_monitoring, args=(camera, modelo), daemon=True)
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

@home.route('/home/editCamera/<camera_id>', methods=['GET', 'POST'])
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

@home.route('/home/deleteCamera/<camera_id>', methods=['GET', 'POST'])
@login_required
def delete_camera(camera_id):
    camera = Camera.objects(id=camera_id).first()
    camera.delete()
    flash('Camera deleted successfully', 'success')
    return redirect(url_for('home.index'))

    
    
    

'''def load_model():
    modelo_ruta = 'D:/Respaldo/Escuela/Proyecto/AlertAI/Artificial_Intelligence/AlertAI.keras'
    
    modelo = load_model(modelo_ruta)
    
    imagen_ruta = 'D:/Respaldo/Escuela/Proyecto/AlertAI/imagen_prueba.jpg'
    
    imagen = image.load_img(imagen_ruta, target_size=(255, 255))
    imagen_array = image.img_to_array(imagen)
    
    imagen_preprocesada = preprocess_input(imagen_array)
    
    print(modelo.predict(np.array([imagen_preprocesada])))'''
        
def start_camera_monitoring(camera, modelo):
    #definir array aqui
    def connect_camera():
        if camera.camera_type == "SecurityCamera":
            cap = cv2.VideoCapture(camera.url)
        else:
            cap = cv2.VideoCapture(0)
            
        if not cap.isOpened():
            notification_queue.put(f"Failed to connect to camera {camera.name}")
            return None
        return cap
    
    def process_frame(cap):
        ret, frame = cap.read()
        if not ret:
            return False
        
        frame_resized = cv2.resize(frame, (255, 255))
        image_array = image.img_to_array(frame_resized)
        imagen_preprocesada = preprocess_input(image_array)
        
        predictions = modelo.predict(np.array([imagen_preprocesada]))
        predicted_classes = np.argmax(predictions, axis=1)
        if predicted_classes != None:
            create_notifications(frame, camera, predicted_classes)
        print(predicted_classes)
        print(camera.name)
        return True

    try:
        cap = connect_camera()
        if cap is None:
            return
        
        active_cameras[camera.name] = cap

        while cap.isOpened():
            if not process_frame(cap):
                notification_queue.put(f'Camera {camera.name} disconnected, attempting to reconnect...')
                time.sleep(.5)  
                cap.release()
                cap = connect_camera()
                active_cameras[camera.name] = cap
                
                if not cap.isOpened() or not process_frame(cap):
                    notification_queue.put(f'Camera {camera.name} disconnected')
                    break
            
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