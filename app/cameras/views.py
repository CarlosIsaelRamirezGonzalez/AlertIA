from . import cameras
from flask_login import login_required, current_user
from flask import render_template, request, redirect, url_for, flash, jsonify
from app.models import CameraData, CameraModel
from app.forms import WebCameraForm, SecurityCameraForm



@cameras.route('/editCamera', methods = ['GET', 'POST'])
@login_required
def add_camera():
    camera_model = CameraModel()
    camera_id = request.args.get('cameraId')
    camera_data = camera_model.get_camera_data(camera_id)
    camera_form = SecurityCameraForm() if camera_data['ip'] == "None" else SecurityCameraForm()

    context = {
        'camera_data' : camera_data,
        'camera_form' : camera_form
    }
    
    return render_template('editCamera.html', **context)


@cameras.route('/deleteCamera', methods = [ 'GET', 'POST'])
@login_required
def delete_camera():
    camera_model = CameraModel()
    try:
        camera_id = request.form.get('camera_id')
        camera_model.delete_camera(camera_id)
        return jsonify({'message': 'Camara eliminada con exito'})
    except Exception as e:
        return jsonify({'error': str(e)})
    


@cameras.route('/registerCamera', methods = ['GET', 'POST'])
@login_required
def register_camera():
    
    camera_type = 'security' if  request.args.get('cameraType') == None else request.args.get('cameraType')
    
    camera_form = WebCameraForm() if camera_type == "web" else SecurityCameraForm()
    
    context = {
        'camera_form' : camera_form,
        'camera_type' : camera_type
    }
    
    alerts = {}
    if camera_form.validate_on_submit():        
        ip_address = 'None' if camera_type != 'security' else  camera_form.ip_address.data 
        address = camera_form.address.data
        place = camera_form.place.data
        camera_name = camera_form.camera_name.data
        phone_number = camera_form.phone_number.data
        alerts["fires"] = camera_form.fires.data
        alerts["bladed_weapons"] = camera_form.bladed_weapons.data
        alerts["stabbing"] = camera_form.stabbing.data
        alerts["handgun"] = camera_form.handgun.data
        alerts["long_gun"] = camera_form.long_gun.data
        alerts["brandishing"] = camera_form.brandishing.data
        alerts["dog_aggression"] = camera_form.dog_aggresion.data
        alerts["car_accident"] = camera_form.car_accident
        alerts["brawls"] = camera_form.brawls.data
        alerts["injured_people"] = camera_form.injured_people.data
        camera_data = CameraData(user_id=current_user.id, ip=ip_address, place=place, camera_type=camera_type,
                                 camera_name=camera_name, settings=alerts, address=address, phone_number=phone_number)
        camera = CameraModel(camera_data=camera_data)
        camera.insert_camera()
        flash("Camara creada con exito")
        return redirect(url_for('WelcomePage'))
        
    return render_template('registerCamera.html', **context)
