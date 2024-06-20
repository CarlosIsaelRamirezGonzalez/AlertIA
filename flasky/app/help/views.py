from flask import render_template
from . import help
from flask_login import login_required


@help.route('/help')
@login_required
def help_page():
    return render_template('help/help.html')