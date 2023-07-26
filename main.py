from app import create_app
from flask import render_template, flash
from flask_login import login_required, current_user
from flask_mail import Mail
#La siguiente linea debe cambiar tambien de lugar
from app.mongo_service import get_cameras

app = create_app()


@app.route('/')
def index():
    flash("The flash works", 'info')
    return render_template('index.html')

@app.route('/WelcomePage', methods=['GET', 'POST'])
@login_required
def WelcomePage():
    # return 'Bienvenido'
    return f'Bienvenido {current_user.id}'

#El codigo proximo soy conciente de que debe ser movido de lugar
cameras_data = get_cameras()
@app.route('/supervisorCameraPanel', methods=['GET', 'POST'])
def supervisorCameraPanel():
    return render_template('supervisorCameraPanel.html', cameras_data = cameras_data)


if __name__ == '__main__':
    app.run()