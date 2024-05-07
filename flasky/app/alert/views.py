from flask import render_template, request, redirect, url_for, flash
from . import alert
from ..models import Notification
from datetime import datetime
from PIL import Image
import cv2
import io
import base64
from flask import request
from mongoengine import Q


@alert.route('/notifications', methods=['GET', 'POST'])
def notifications():
    if request.method == 'POST':
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error al abrir la cámara")
            
        ret, frame = cap.read()
        
        if not ret:
            print("Error al capturar la imagen")

        image = Image.fromarray(frame)
        output = io.BytesIO()
        image.save(output, format='PNG')
        image_data_compressed = output.getvalue()
        
        
        notificacion = Notification(
            user = "enriquerc260@gmail.com",
            date_time=datetime.utcnow(),
            place='Lugar por defecto',  
            threat='Ataque de perros',  
            camera_name='Camara 2', 
            certainty='Certeza por defecto',
            image=image_data_compressed 
        )
        notificacion.save()
        cap.release()
        flash('Alerta creada correctamente', 'success')
        
    load_notifications = Notification.objects(user="enriquerc260@gmail.com")
        
    return render_template('alert/notifications.html', load_notifications = load_notifications)

@alert.route('/notifications/delete/<notification_id>', methods=['POST'])
def delete_notification(notification_id):
    notification = Notification.objects.get(id=notification_id)
    print(notification_id)
    notification.delete()
    flash('Notificación eliminada correctamente', 'success')
    return redirect(url_for('alert.notifications'))

@alert.route('/notifications/search_notifications', methods=['GET', 'POST'])
def search():
    filter_value = request.form.get('search', '')
    if filter_value == '':
        return redirect(url_for('alert.notifications'))
    
    
    load_notifications = Notification.objects.filter(Q(place__icontains=filter_value) |
                                                     Q(threat__icontains=filter_value) |
                                                     Q(camera_name__icontains=filter_value) |
                                                     Q(certainty__icontains=filter_value),
                                                     user="enriquerc260@gmail.com")
    
    return render_template('alert/notifications.html', load_notifications = load_notifications)
    
@alert.route('/notifications/view/<notification_id>', methods=['GET', 'POST'])
def view_notification(notification_id):
    load_notification = Notification.objects.get(id=notification_id)
    if load_notification.read == False:
        load_notification.update(set__read=True)
    image_base64 = base64.b64encode(load_notification.image).decode('utf-8')
    load_notification.image = image_base64
    return render_template('alert/details.html', load_notification=load_notification)
