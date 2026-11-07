"""Decoradores de las vistas: permisos de administrador y protección de acciones."""

from functools import wraps

from flask import abort, current_app, request
from flask_login import current_user
from flask_wtf.csrf import ValidationError, validate_csrf


def admin_required(f):
    """Solo deja pasar al administrador (el correo de `FLASKY_ADMIN`); a los demás les responde 403.

    Args:
        f: Vista que se protege.

    Returns:
        La vista protegida.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Revisa el correo antes de correr la vista."""
        if current_user.email != current_app.config['FLASKY_ADMIN']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def csrf_post(f):
    """Solo acepta POST con el token CSRF de la página, para que otro sitio no pueda borrar datos.

    Args:
        f: Vista que se protege.

    Returns:
        La vista protegida: responde 405 si no es POST y 400 si el token no es válido.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Revisa el método y el token antes de correr la vista."""
        if request.method != 'POST':
            abort(405)
        try:
            validate_csrf(request.form.get('csrf_token'))
        except ValidationError:
            abort(400)
        return f(*args, **kwargs)
    return decorated_function
