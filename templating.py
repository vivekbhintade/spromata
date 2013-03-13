from util import *
import config
import re
from jinja2 import Environment, BaseLoader, TemplateNotFound, Markup
import pystache

def spromata_view_dir():
    return os.path.join(spromata_root(), 'views')
bottle.TEMPLATE_PATH.append(spromata_view_dir())
SPROMATA_VIEW_DIR = spromata_view_dir()

class ReloadingLoader(BaseLoader):
    def get_source(self, environment, template_name):
        if len(template_name.split('.'))<2: template_name += '.html'
        filepath = os.path.join('views', template_name)
        if not os.path.exists(filepath): filepath = os.path.join(SPROMATA_VIEW_DIR, template_name)
        if not os.path.exists(filepath): raise TemplateNotFound(template_name)
        f = open(filepath)
        contents = f.read()
        f.close()
        mtime = os.path.getmtime(filepath)
        def uptodate():
            try: return os.path.getmtime(filepath) == mtime
            except: return False
        return contents, filepath, uptodate

def timestamp_to_nicedate(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%b %d, %Y @ %I:%M %p")
def timestamp_to_local_date(time):
    return local_date(time)
def timestamp_to_prettydate(timestamp):
    return pretty_date(timestamp)
def sanitize_text(data):
    if not data: return ''
    p = re.compile(r'<.*?>')
    d = data
    try:
        #print "GOING 1"
        #d = unicode(d)
        d = d.encode('latin1','replace').decode('utf8','ignore')
    except:
        #print "GOING 2"
        d = d.encode('latin1', 'ignore').decode('utf8', 'ignore')
        #d = d.encode('utf8', 'ignore').decode('utf8')
    d = p.sub('', d)
    d = d.replace('\\', '')
    d = d.replace('>', '')
    d = d.replace('<', '')
    return d
jinja2_filters = {
    'to_nicedate': timestamp_to_nicedate,
    'to_local_date': timestamp_to_local_date,
    'to_prettydate': timestamp_to_prettydate,
    'sanitize': sanitize_text,
}
jinja2_env = Environment(loader=ReloadingLoader())
jinja2_env.filters.update(**jinja2_filters)

def render_jinja2(template, **context):
    return jinja2_env.get_template(template).render(**context)
    print "LETS RENDER"
    rendered = bottle.template(template, template_adapter=bottle.Jinja2Template, template_settings={'cache_size': 0, 'autoescape':True}, **context)
    print "YEA RENDERING"
    return rendered

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

