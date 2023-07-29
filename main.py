from app import create_app
from flask import render_template, flash
from flask_login import login_required, current_user
from flask_mail import Mail

app = create_app()


@app.route('/')
def index():
    flash("Mensaje de exito", "success")
    return render_template('index.html')

@app.route('/WelcomePage', methods=['GET', 'POST'])
@login_required
def WelcomePage():
    # return 'Bienvenido'
    return f'Bienvenido {current_user.id}'



if __name__ == '__main__':
    app.run()