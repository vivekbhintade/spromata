import bottle
from functools import partial
from spromata.core.auth import *
from spromata.templating import *
from spromata.util import *

# first define the functional elements
# then the render/response pieces
# then string them together
def create_rest_api(base_collection, url_base, restricted=False, override_={}, post_={}):
    def list_collection(**context):
        collection = base_collection.fetch(**context)
        bottle.response.context.update({'collection': collection})
        return collection
    def update_collection(**context): pass
    def add_to_collection(**context):
        new_item = bottle.request.json
        new_item['user'] = context['user']
        item = base_collection.new(**new_item)
        bottle.response.context.update({'item': item})
        return item
    def delete_collection(**context): pass
    def show_item(id, **context):
        item = base_collection.get(_id=id)
        bottle.response.context.update({'item': item})
        return item
    def update_item(id, **context):
        updated_item = bottle.request.json
        updated_item['_id'] = id
        item = base_collection.update(**updated_item)
        bottle.response.context.update({'item': item})
        return item
    def add_to_item(id, **context): pass
    def delete_item(id, **context):
        base_collection.remove(_id=id)
        return list_collection(**context)
    route_map = {
        # Collections
        '%s' % url_base: list_collection,
        '>%s' % url_base: update_collection,
        '#%s' % url_base: add_to_collection,
        'X%s' % url_base: delete_collection,
        # Entities
        '%s/:id' % url_base: show_item,
        '>%s/:id' % url_base: update_item,
        '#%s/:id' % url_base: add_to_item,
        'X%s/:id' % url_base: delete_item,
    }
    template_map = {
        # Collections
        list_collection: 'list',
        update_collection: 'list',
        add_to_collection: 'show',
        delete_collection: 'list',
        # Entities
        show_item: 'show',
        update_item: 'show',
        add_to_item: 'show',
        delete_item: 'list',
    }

    # Create the full callback for a route and action
    def make_templated_callback(callback):
        template_base = 'generic/'
        def wrapper(**context):
            print context
            context['user'] = bottle.response.context.user.id
            cb=callback
            if override_.has_key(callback.__name__): cb = override_[callback.__name__]
            result = cb(**context)
            if post_.has_key(callback.__name__): result = post_[cb.__name__](**result)
            return render(template_base + template_map[callback], **result)
        if restricted: wrapper = require_auth(wrapper)
        return wrapper
    # Make a JSON version too
    def make_json_callback(callback):
        def wrapper(**context):
            context['user'] = bottle.response.context.user.id
            cb=callback
            if override_.has_key(callback.__name__): cb = override_[callback.__name__]
            print "CONTEXT: %s" % context
            result = cb(**context)
            if post_.has_key(callback.__name__): result = post_[cb.__name__](**result)
            print "RESULT: %s" % result
            return pymongo_to_json(result)
        if restricted: wrapper = require_auth(wrapper)
        return wrapper

    # Generate the routes
    for route in route_map.items():
        path, callback = route
        if path.startswith('#'):
            bottle.post(path[1:] + '.json')(make_json_callback(callback))
            bottle.post(path[1:])(make_templated_callback(callback))
        elif path.startswith('X'):
            bottle.delete(path[1:] + '.json')(make_json_callback(callback))
            bottle.delete(path[1:])(make_templated_callback(callback))
        elif path.startswith('>'):
            bottle.put(path[1:] + '.json')(make_json_callback(callback))
            bottle.put(path[1:])(make_templated_callback(callback))
        else:
            bottle.get(path + '.json')(make_json_callback(callback))
            bottle.get(path)(make_templated_callback(callback))

