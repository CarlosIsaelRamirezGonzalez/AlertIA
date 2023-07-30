from app import create_app
from flask import render_template, flash
from flask_login import login_required, current_user
from flask_mail import Mail
#La siguiente linea debe cambiar tambien de lugar
from app.mongo_service import get_cameras

app = create_app()


@app.route('/')
def index():
    flash("Mensaje de exito", "success")
    return render_template('index.html')

@app.route('/WelcomePage', methods=['GET', 'POST'])
@login_required
def WelcomePage():
    return f'Bienvenido {current_user.id}'


@app.route('/supervisorCameraPanel', methods=['GET', 'POST'])
def supervisorCameraPanel():
    cameras_data = get_cameras()
    return render_template('supervisorCameraPanel.html', cameras_data = cameras_data)


if __name__ == '__main__':
    app.run()