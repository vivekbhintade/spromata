import bottle
import os
from jinja2 import Environment, BaseLoader, TemplateNotFound, Markup

""" Some handy things without requiring a whole config.py etc."""

class ReloadingLoader(BaseLoader):
    def get_source(self, environment, template_name):
        if len(template_name.split('.'))<2: template_name += '.html'
        filepath = os.path.join('views', template_name)
        if not os.path.exists(filepath): raise TemplateNotFound(template_name)
        f = open(filepath)
        contents = f.read()
        f.close()
        mtime = os.path.getmtime(filepath)
        def uptodate():
            try: return os.path.getmtime(filepath) == mtime
            except: return False
        return contents, filepath, uptodate

@bottle.hook('before_request')
def create_context(): bottle.response.context = {}

jinja2_env = Environment(loader=ReloadingLoader())
def render_jinja2(template, **context):
    return jinja2_env.get_template(template).render(**context)
    rendered = bottle.template(template, template_adapter=bottle.Jinja2Template, template_settings={'cache_size': 0, 'autoescape':True}, **context)
    return rendered

renderer = render_jinja2
def render(template, **context):
    full_context = dict(context.items() + bottle.response.context.items())
    return renderer(template, **full_context)

@bottle.get('/<filename:path>')
def static(filename):
    return bottle.static_file(filename, root='static')

