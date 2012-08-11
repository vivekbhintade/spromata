from util import *
import config
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
def removeTags(html):
    soup = BeautifulSoup(html)
    for tag in ['a','script','link','div','form']:
        for tag in soup.findAll(tag):
            tag.replaceWith("")
    return str(soup)
jinja2_filters = {
    'to_nicedate': timestamp_to_nicedate,
    'sanitize': strip_tags
}
jinja2_env = Environment(loader=ReloadingLoader())
jinja2_env.filters.update(**jinja2_filters)


def render_jinja2(template, **context):
    return jinja2_env.get_template(template).render(**context)
    return bottle.template(template, template_adapter=bottle.Jinja2Template, template_settings={'cache_size': 0, 'autoescape':True}, **context)

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

