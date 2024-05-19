from flask import render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from ..models import Camera
from .forms import AddCameraForm
from . import home
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input



@home.route('/home')
@login_required
def index():
    
    cameras = Camera.objects(user=current_user.id).all()
    
    
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

