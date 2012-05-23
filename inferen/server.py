import bottle
import pymongo
import json
from meta_server import *
from data import *
from resources import *
from utils import *
import config

#-----
# Main views
#-----

if not nodes.get(name='root'): nodes.new(name='root')

def index(**context):
    root = nodes.get(name='root')
    root['items'] = root.to_
    context['root'] = root
    return render('list', **context)

def show_node(node_id, **context):
    node = nodes.get(_id=node_id)
    node['items'] = node.to_
    context['root'] = root
    return render('list', **context)

#-----
# Node views
#-----

def get_node(node_id, **context):
    node_path_parts = node_id.split('/')
    if len(node_path_parts) == 1:
        node = nodes.get(_id=node_path_parts[0])
    elif len(node_path_parts) > 2:
        source = sources[node_path_parts[0]]
        resource = source.resources[node_path_parts[1]]
        if len(node_path_parts) == 3:
            node = resource.get(node_path_parts[2])
        elif len(node_path_parts) == 4:
            parent_node = resource.get(node_path_parts[2])
            node = parent_node.__getattr__(node_path_parts[3])
    else: return bottle.error404()
    node_rep = make_node_rep(node, 2)
    return pymongo_to_json(node_rep)

def new_node(**context):
    new_node_attrs = {}
    new_node_attrs['name'] = bottle.request.json.get('name')
    if bottle.request.json.has_key('type'): new_node_attrs['type'] = bottle.request.json.get('type')
    new_node = nodes.new(**new_node_attrs)
    from_node = nodes.get(_id=bottle.request.json.get('from_'))
    from_node.to_ = new_node
    return pymongo_to_json(make_node_rep(new_node, 2))

def update_node(node_id, **context):
    node = nodes.get(_id=node_id)
    new_name = bottle.request.json.get('name')
    new_type = bottle.request.json.get('type')
    new_from_ = bottle.request.json.get('from_')
    if new_name:
        node['name'] = new_name
        nodes.update(**node)
    if new_type:
        node['type'] = new_type
        nodes.update(**node)
    if new_from_:
        edges.remove(to_=node.id)
        from_node = nodes.get(_id=new_from_)
        node.from_ = from_node
    return pymongo_to_json(make_node_rep(node))

def delete_node(node_id, **context):
    node = nodes.get(_id=node_id)
    edges.remove(to_=node.id)
    edges.remove(from_=node.id)
    nodes.remove(**node)

#-----
# Route configuration
#-----

_node_id_ = "<node_id:re:[a-zA-Z0-9/_]+>"
route_map = {
    '/': index,

    '#/nodes/new': new_node,
    '/nodes/'+_node_id_+'/': show_node,
    '/nodes/'+_node_id_: get_node,
    '>/nodes/'+_node_id_: update_node,
    'X/nodes/'+_node_id_: delete_node,
}

# Define routes from the route map
def make_route_callback(callback):
    if type(callback) == list: callback = partial(*callback)
    def wrapper(**context):
        return callback(**get_session(**start_context(**context)))
    return wrapper

for route in route_map.items():
    path, callback = route
    if path.startswith('#'):
        bottle.post(path[1:])(make_route_callback(callback))
    elif path.startswith('X'):
        bottle.delete(path[1:])(make_route_callback(callback))
    elif path.startswith('>'):
        bottle.put(path[1:])(make_route_callback(callback))
    else:
        bottle.get(path)(make_route_callback(callback))

# Static fallback
@bottle.route('/<filepath:path>')
def static_file(filepath):
    return bottle.static_file(filepath, root='./static/')

# Run the server
bottle.debug(config.debug)
bottle.run(server=config.server, host='0.0.0.0', port=config.port, reloader=config.debug)

