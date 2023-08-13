from . import cameras
from flask_login import login_required
from flask import render_template, session, request, redirect, url_for
from app.models import CameraData
from app.forms import RegisterCamera
from app.helpers import delete_sessions

@cameras.route('/registerCamera', methods = ['GET', 'POST'])
@login_required
def register_camera():
    register_camara_form = RegisterCamera()
    camera_type = session['camera_type']
    
    # Acabo de arregalr el bug de la manera mas puerca posible, PERO funciona 
    if camera_type is None:
        return redirect(url_for('cameras.register_camera'))
    context = {
        'register_camera_form' : register_camara_form,
        'camera_type' : camera_type
    }
    
    # delete_sessions(['camera_type'])
    
    return render_template('registerCamera.html', **context)
