""" Authentification handling.
This is taken from 
http://flask.pocoo.org/snippets/8/
"""

from functools import wraps

import flask as fk

from ..models import UserModel


def check_auth(username, password):
    """This function is called to check if a email /
    password combination is valid.
    """
    user = UserModel.objects(email=username).first()
    if user is None:
        return False
    else:
        fk.g.user = user
        return True

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return fk.Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = fk.request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
