from flask_login import login_required, current_user
from flask import render_template
from . import main  

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

