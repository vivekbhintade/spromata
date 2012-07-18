from spromata.util import *
import config
from jinja2 import Environment, FunctionLoader, ChoiceLoader, FileSystemLoader
import pystache

def spromata_view_dir():
    return os.path.join(spromata_root(), 'views')
bottle.TEMPLATE_PATH.append(spromata_view_dir())

def render_jinja2(template, **context):
    return bottle.template(template, template_adapter=bottle.Jinja2Template, template_settings={'cache_size': 0}, **context)

mustacher = pystache.Renderer(search_dirs=['views'], file_extension='html')
def render_mustache(template, **context):
    return mustacher.render(mustacher.load_template(template), context)

renderer = render_jinja2
def render(template, **context):
    full_context = dict(context.items() + bottle.response.context.items())
    return renderer(template, **full_context)

def message(message_text, **context):
    context['message'] = message_text
    return render('message', **context)

