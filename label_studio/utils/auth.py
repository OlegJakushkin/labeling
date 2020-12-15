from functools import wraps
from flask import request, Response, render_template
from flask_login import current_user

USERNAME = 'ls'
PASSWORD = ''


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == USERNAME and password == PASSWORD



def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if PASSWORD and (not auth or not check_auth(auth.username, auth.password)):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def approved_for_import(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(current_user.can_import())
        if not current_user.can_import():
            return render_template('forbidden.html', role="Import")
        return f(*args, **kwargs)
    return decorated

def approved_for_export(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(current_user.can_export())
        if not current_user.can_export():
            return render_template('forbidden.html', role="Export")
        return f(*args, **kwargs)
    return decorated  

def approved_for_labeling(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(current_user.can_label())
        if not current_user.can_label():
            return render_template('forbidden.html', role="Labeling")
        return f(*args, **kwargs)
    return decorated 
