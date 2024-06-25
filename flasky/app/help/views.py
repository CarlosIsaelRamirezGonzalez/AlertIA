from flask import render_template, flash, redirect, url_for
from . import help
from ..email import send_email
from .forms import ReportProblemEmailForm
from flask_login import login_required, current_user


@help.route('/help')
@login_required
def help_page():
    return render_template('help/help.html')


@help.route('/report_support', methods=['GET', 'POST'])
@login_required
def report_support():
    form = ReportProblemEmailForm()
    if form.validate_on_submit():
        general_description = form.general_description.data
        description = form.description.data
        send_email("alertia2023@gmail.com", 'Error.', 'help/email/report_problem', general_problem = general_description, problem = description,
                   username = current_user.username) # Poner el gmail como variable del entorno
        flash("Report send succesfully")
        return redirect(url_for('help.help_page'))
    return render_template('help/report_problem.html', form = form)