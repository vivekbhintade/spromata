from spromata.util import *
from core.data import *

def is_auth():
    context = bottle.response.context
    return context['session'] and context['user']

def require_is(is_type):
    def meta_wrapper(f):
        def wrapper(*args, **kwargs):
            if (is_auth() and bottle.response.context.user.type == is_type): return f(*args, **kwargs)
            return bottle.redirect('/login?next=%s' % bottle.request.path)
        return wrapper
    return meta_wrapper

def require_auth(f):
    def wrapper(*args, **kwargs):
        if is_auth(): return f(*args, **kwargs)
        return bottle.redirect('/login?next=%s' % bottle.request.path)
    return wrapper

def is_admin():
    context = bottle.response.context
    return is_auth() and context['user'].type=='admin'

def require_admin(f):
    def wrapper(*args, **kwargs):
        if is_admin(): return f(*args, **kwargs)
        return bottle.redirect('/')
    return wrapper
    
def add_session(context):
    context['session'] = None
    context['user'] = None
    session_user = bottle.request.get_cookie("user", secret=config.session_secret)
    session_token = bottle.request.get_cookie("token", secret=config.session_secret)
    if session_user and session_token:
        session = sessions.get(user=session_user, token=session_token)
        if session:
            if session.timeout and session.timeout < datetime.datetime.now():
                context['errors'].append("Your session has timed out.")
                return context
            context['session'] = session
            context['user'] = session.user.typed()
            return context
    return context

