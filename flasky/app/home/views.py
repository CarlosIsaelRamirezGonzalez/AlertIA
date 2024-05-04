from flask import render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from ..models import Camera
from .forms import AddCameraForm
from . import home

@home.route('/home')
@login_required
def index():
    return render_template('home/home.html')

@home.route('/addCamera')
@login_required
def add_camera():
    form = AddCameraForm()
    
    if form.validate_on_submit():
        
        # Create model
        camera = Camera(name=form.name.data, phone_number=form.phone_number.data,
                        security=form.security.data, ip=form.ip.data, place=form.place.data, address=form.address.data)
        
        if form.place.data != 'Personalized':
            camera.insert_alerts(form.place.data)
        else:
            camera.insert_alerts(alerts=camera.alerts)
        
        # save model
        camera.save()
        flash("Camera saved successfully")
        return redirect(url_for('home.index'))        

                
    return render_template('home/add-camera.html')