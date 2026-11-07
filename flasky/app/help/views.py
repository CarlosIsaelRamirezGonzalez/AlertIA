"""Vistas de ayuda."""

from flask import current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import help
from ..email import send_email
from .forms import ReportProblemEmailForm


@help.route('/help')
@login_required
def help_page():
    """Muestra la página de ayuda.

    Returns:
        La página.
    """
    return render_template('help/help.html')


@help.route('/report_support', methods=['GET', 'POST'])
@login_required
def report_support():
    """Muestra el formulario de problemas y, al enviarlo, lo manda por correo a soporte.

    Returns:
        El formulario, o una redirección a la ayuda si se envió.
    """
    form = ReportProblemEmailForm()
    if form.validate_on_submit():
        send_email(current_app.config['SUPPORT_EMAIL'], 'Error.', 'help/email/report_problem',
                   general_problem=form.general_description.data,
                   problem=form.description.data,
                   username=current_user.username)
        flash("Report send succesfully")
        return redirect(url_for('help.help_page'))
    return render_template('help/report_problem.html', form=form)
