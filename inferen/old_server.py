import bottle
import pymongo
import datetime
import json
import jinja2
import re
import markdown
from meta_server import *
from data import *
from utils import *

@bottle.get('/')
def index():
    return bottle.redirect('/pages/Home')

attributes = {
    'page': ['name', 'contents'],
}
collections = {
    'pages': make_collection('pages')(),
}
def define_resource(type, key_name):
    collection = collections[type]

    # Helpers
    def get_(key): return collection.get(**{key_name: key})
    def get_all(): return collection.fetch()
    def context_(item):
        all_items = get_all()
        return {'type': type, type: item, 'all_%ss' % type: all_items}

    # Views
    @bottle.get('/%ss' % type)
    def list_():
        return render('list_%ss' % type, **context_(None))
    @bottle.get('/%ss/new' % type)
    def new_(**kwargs):
        key = kwargs[key_name]
        item = {key_name: key}
        return render('new_' + type, **context_(item))
    @bottle.get('/%ss/:%s' % (type, key_name))
    def show_(**kwargs):
        key = kwargs[key_name]
        item = get_(key)
        if item: return render('show_' + type, **context_(item))
        else: return new_(**{key_name: key})
    @bottle.get('/%ss/:%s/edit' % (type, key_name))
    def edit_(**kwargs):
        key = kwargs[key_name]
        item = get_(key)
        if item: return render('edit_' + type, **context_(item))
        else: return new_(**{key_name: key})
    @bottle.post('/%ss/:%s/update' % (type, key_name))
    def update_(**kwargs):
        key = kwargs[key_name]
        item = get_(key)
        if not item: item = collection.new(**{key_name: key})
        new_attributes = {}
        for attribute_name in attributes[type]:
            attribute_value = bottle.request.forms.get('%s_%s' % (type, attribute_name))
            if attribute_value:
                new_attributes[attribute_name] = attribute_value
        if new_attributes:
            item.update(**new_attributes)
            collection.update(**item)
        return bottle.redirect('/%ss/%s' % (type, key))
    @bottle.get('/%ss/:%s/delete' % (type, key_name))
    def delete_(**kwargs):
        key = kwargs[key_name]
        item = get_(key)
        collection.remove(**item)
        return bottle.redirect('/%ss' % (type))

define_resource('page', 'name')
define_resource('template', 'name')

#@bottle.get('/templates/')
#def list_templates():
#    templates = templates.fetch()
#    context = { 'templates': templates, }
#    return render('list_templates', **context)
#
#@bottle.post('/templates/:template_name/save')
#def save_template(template_name):
#    template_key = bucket.get_key('%s.template' % page_name)
#    template_contents = bottle.request.forms.get('template_contents')
#    if template_key and template_contents:
#        template_key.set_contents_from_string(template_contents)
#    return bottle.redirect('/templates/%s' % template_name)

# Static fallback
@bottle.route('/<filepath:path>')
def static_file(filepath):
    return bottle.static_file(filepath, root='./static/')

bottle.debug(config.debug)
bottle.run(server=config.server, host='0.0.0.0', port=config.port, reloader=config.debug)
