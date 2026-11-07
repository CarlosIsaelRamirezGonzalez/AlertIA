"""Vista de la página pública."""

from flask import render_template

from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    """Muestra la página de presentación de AlertAI.

    Returns:
        La página.
    """
    return render_template('index.html')
