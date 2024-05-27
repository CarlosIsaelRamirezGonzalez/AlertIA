from flask import render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from ..models import Camera
from .forms import AddCameraForm
from ..decorators import post_only
from . import home

@home.route('/home')
@login_required
def index():
    cameras = Camera.objects(user=current_user.id).all()    
    
    return render_template('home/home.html', cameras=cameras)

@home.route('/deleteCamera/<id_camera>', methods=["GET", "POST"])
@login_required
@post_only
def delete_camera(id_camera):
    try:
        camera = Camera.objects(id=id_camera)
        camera.delete()
        return 200
    except: 
        return 404

@home.route('/addCamera', methods=['GET', 'POST'])
@login_required
def add_camera():
    form = AddCameraForm()
    
    if form.validate_on_submit():
        
        # Create model
        camera = Camera(name=form.name.data, phone_number=form.phone_number.data,
                        security=form.security.data, ip=form.ip.data, place=form.place.data,
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