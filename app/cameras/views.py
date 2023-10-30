from . import cameras
from flask_login import login_required, current_user
from flask import render_template, session, request, redirect, url_for, flash, jsonify
from app.mongo_service import delete_camera_by_id
from app.models import CameraData, CameraModel
from app.forms import RegisterCamera
from app.helpers import delete_sessions



@cameras.route('/deleteCamera', methods = [ 'GET', 'POST'])
@login_required
def delete_camera():
    try:
        camera_id = request.form.get('camera_id')
        delete_camera_by_id(camera_id)
        return jsonify({'message': 'Camara eliminada con exito'})
    except Exception as e:
        return jsonify({'error': str(e)})
    


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
    alerts = {}
    if register_camara_form.validate_on_submit():
        if camera_type != "security":
            ip_address = 'None'
        else :
            ip_address = register_camara_form.ip_address.data # Verificar que si haya ingresado algo
        address = register_camara_form.address.data
        place = register_camara_form.place.data
        camera_name = register_camara_form.camera_name.data
        phone_number = register_camara_form.phone_number.data
        alerts["fires"] = register_camara_form.fires.data
        alerts["bladed_weapons"] = register_camara_form.bladed_weapons.data
        alerts["stabbing"] = register_camara_form.stabbing.data
        alerts["handgun"] = register_camara_form.handgun.data
        alerts["long_gun"] = register_camara_form.long_gun.data
        alerts["brandishing"] = register_camara_form.brandishing.data
        alerts["dog_aggression"] = register_camara_form.dog_aggresion.data
        alerts["car_accident"] = register_camara_form.car_accident.data
        alerts["brawls"] = register_camara_form.brawls.data
        alerts["injured_people"] = register_camara_form.injured_people.data
        # Hacer logica para ingresar los datos en la base de datos
        camera_data = CameraData(user_id=current_user.id, ip=ip_address, place=place, camera_type=camera_type,
                                 camera_name=camera_name, settings=alerts, address=address, phone_number=phone_number)
        camera = CameraModel(camera_data=camera_data)
        camera.insert(camera_data)
        flash("Camara creada con exito")
        return redirect(url_for('WelcomePage'))
    
    # delete_sessions(['camera_type'])
    
    
    return render_template('registerCamera.html', **context)
