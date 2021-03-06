from util import *
import config
import re
from jinja2 import Environment, BaseLoader, TemplateNotFound, Markup
import pystache
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

SPROMATA_VIEW_DIR = os.path.join(spromata_root(), 'views')
bottle.TEMPLATE_PATH.append(SPROMATA_VIEW_DIR)

class ReloadingLoader(BaseLoader):
    def get_source(self, environment, template_name):
        if len(template_name.split('.'))<2: template_name += '.html'
        if hasattr(config, 'template_path'):
            filepath = os.path.join(config.template_path, template_name)
        else:
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

# Formatting filters

# - Time

def timestamp_to_nicedate_notime(timestamp):
    return timestamp_to_nicedate(timestamp, False)
def timestamp_to_nicedate(timestamp, incl_time=True):
    if type(timestamp) in (int, float):
        d = datetime.datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp,datetime.datetime):
        d = timestamp
    date_format = "%b %d, %Y"
    if incl_time: date_format += " @ %I:%M %p"
    return d.strftime(date_format)
def timestamp_to_local_date(timestamp):
    return local_date(timestamp)
def timestamp_to_prettydate(timestamp):
    return pretty_date(timestamp)

# - Money and other numbers

def format_bigint(value):
    return locale.format("%d", value, grouping=True)

def format_currency(value, with_space=False):
    return "$%s%s" % (' ' if with_space else '', locale.format("%.2f", value, grouping=True))

# Conversion filters

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

from spromata.util import pymongo_to_json
def to_json_str(ob):
    return json.dumps(pymongo_to_json(ob))

jinja2_filters = {
    'to_nicedate': timestamp_to_nicedate,
    'to_nicedate_notime': timestamp_to_nicedate_notime,
    'to_local_date': timestamp_to_local_date,
    'to_prettydate': timestamp_to_prettydate,
    'sanitize': sanitize_text,
    'to_json': pymongo_to_json,
    'to_json_str': to_json_str,
    'format_bigint': format_bigint,
    'format_currency': format_currency,
}
jinja2_env = Environment(loader=ReloadingLoader(), extensions=["jinja2.ext.do",])
jinja2_env.filters.update(**jinja2_filters)

def render_jinja2(template, **context):
    return jinja2_env.get_template(template).render(**context)
    rendered = bottle.template(template, template_adapter=bottle.Jinja2Template, template_settings={'cache_size': 0, 'autoescape':True}, **context)
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

