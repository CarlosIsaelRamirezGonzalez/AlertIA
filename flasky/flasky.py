"""Punto de entrada de la aplicación: `flask run` y `flask test` empiezan aquí."""

import os

import click
from dotenv import load_dotenv

# Lee las variables de .env, si existe. Ver .env.example.
load_dotenv()

from app import create_app, db  # noqa: E402 - después de cargar .env
from app.models import User, Camera  # noqa: E402

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    """Deja la base y los modelos listos en `flask shell`.

    Returns:
        Los objetos disponibles; Flask exige un diccionario, así que se arma solo aquí.
    """
    return {'db': db, 'User': User, 'Camera': Camera}


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Corre las pruebas: todas, o solo las que se indiquen.

    Args:
        test_names: Pruebas por nombre, como `tests.test_detection`; vacío corre todas.
    """
    import unittest

    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(list(test_names))
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
