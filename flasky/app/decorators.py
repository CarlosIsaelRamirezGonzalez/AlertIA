from functools import wraps
from flask import abort, current_app, request, jsonify
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.email != current_app.config['FLASKY_ADMIN']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def post_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method != 'POST':
            return jsonify({'error': 'Method not allowed.'}), 405
        return f(*args, **kwargs)
    return decorated_function