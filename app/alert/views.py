from flask import render_template, request, redirect, url_for, flash
from . import alert
from ..models import Notification
from datetime import datetime
from PIL import Image
import cv2
import io
import base64

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
            threat='Amenaza por defecto',  
            camera_name='Nombre de Cámara', 
            certainty='Certeza por defecto',
            image=image_data_compressed 
        )
        notificacion.save()
        cap.release()
        flash('Alerta creada correctamente', 'success')
        
    load_notifications = Notification.objects(user="enriquerc260@gmail.com")
    #TODO cambiar la carga de la imagen de lugar para que solo haga la reconstruccion al querer ver mas detalles de la 
    #notificacion
    
    for notification in load_notifications:
        image_base64 = base64.b64encode(notification.image).decode('utf-8')
        notification.image = image_base64
        
    return render_template('alert/notifications.html', load_notifications = load_notifications)

@alert.route('/notifications/delete/<notification_id>', methods=['POST'])
def delete_notification(notification_id):
    notification = Notification.objects.get(id=notification_id)
    print(notification_id)
    notification.delete()
    flash('Notificación eliminada correctamente', 'success')
    return redirect(url_for('alert.notifications'))