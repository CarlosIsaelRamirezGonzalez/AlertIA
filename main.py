from app import create_app
from flask import render_template, flash
from flask_login import login_required, current_user
from app.models import CameraModel
from app.forms import WebCameraForm, SecurityCameraForm

app = create_app()

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/WelcomePage', methods=['GET', 'POST'])
@login_required
def WelcomePage():
    
    camera_model = CameraModel()
    cameras = camera_model.get_cameras_by_user(current_user.id)
    context = {
        'username': current_user.username,
        'cameras': cameras
    }
    flash("Registro exitoso", "success")
    return render_template('welcomepage.html', **context)


@app.route('/supervisorCameraPanel', methods=['GET', 'POST'])
def supervisorCameraPanel():
    camera_model = CameraModel()
    cameras_data = camera_model.get_cameras()
    return render_template('supervisorCameraPanel.html', cameras_data = cameras_data)


if __name__ == '__main__':
    app.run()