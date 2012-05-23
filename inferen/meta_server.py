import bottle
import jinja2
from data import *
from functools import partial
import config

class Context(Document): pass

def message(message_text, **context):
    context['message'] = message_text
    return render('message', **context)

def start_context(**context):
    context['messages'] = []
    context['errors'] = []
    context['submitted'] = defaultdict(str)
    context['timestamp'] = time.time()
    context['config'] = config
    return context

def get_session(**context):
    context['session'] = None
    context['user'] = None
    session_user = bottle.request.get_cookie("user", secret=config.secret)
    session_token = bottle.request.get_cookie("token", secret=config.secret)
    if session_user and session_token:
        session = sessions.get(user=session_user, token=session_token)
        if session:
            context['session'] = session
            context['user'] = session.user
            return context
    return context

def authenticate(f, **context):
    if context['session'] and context['user']:
        return f(**context)
    return bottle.redirect('/login?next=%s' % bottle.request.path)

class MongoLoader(jinja2.BaseLoader):
    def __init__(self, collection):
        self.collection = collection
    def get_source(self, environment, template_name):
        template = self.collection.get(name = template_name)
        if not template:
            template_type = template_name.split('_')[-1]
            if template_type:
                return self.get_source(environment, template_type)
            raise jinja2.TemplateNotFound(template_name)
        template_source = template.contents
        return template_source, template_name, lambda: True
jinja_mongo_environment = jinja2.Environment(loader=MongoLoader(templates))

def render(template, **context):
    return bottle.jinja2_template(template, **context)
def render_mongo(template, **context):
    return jinja_mongo_environment.get_template(template).render(**context)

def renderer(template, **base_context):
    def wrapper(**context):
        return render(template, **dict(base_context.items() + context.items()))
    return wrapper
