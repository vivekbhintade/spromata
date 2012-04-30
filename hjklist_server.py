import bottle
import pymongo
import json
from meta_server import *
from hjklist_data import *

root = nodes.get(name='root')
root['items'] = root.to_

@bottle.get('/')
def index():
    context = {'root': pymongo_to_json(make_node_rep(root, 2))}
    return bottle.jinja2_template('hjklist', context)

@bottle.post('/new')
def new_node():
    new_node = nodes.new(name=bottle.request.json.get('name'))
    print bottle.request.forms.get('from_')
    from_node = nodes.get(_id=bottle.request.json.get('from_'))
    from_node.to_ = new_node
    return pymongo_to_json(make_node_rep(new_node))

@bottle.delete('/<node_id:re:[a-zA-Z0-9]+>')
def delete_node(node_id):
    node = nodes.get(_id=node_id)
    edges.remove(to_=node.id)
    edges.remove(from_=node.id)
    nodes.remove(**node)

@bottle.get('/<node_id:re:[a-zA-Z0-9]+>')
def show_node(node_id):
    node = nodes.get(_id=node_id)
    node_rep = make_node_rep(node, 2)
    return pymongo_to_json(node_rep)

@bottle.get('/<node_id:re:[a-zA-Z0-9]+>/to')
def show_to_(node_id):
    node = nodes.get(_id=node_id)
    node_reps = [make_node_rep(n) for n in node.to_]
    return pymongo_to_json(node_reps)

@bottle.get('/<node_id:re:[a-zA-Z0-9]+>/from')
def show_from_(node_id):
    node = nodes.get(_id=node_id)
    return pymongo_to_json(node.from_)

@bottle.post('/<node_id>/add')
def add_node(node_id):
    node = nodes.get(_id=node_id)
    new_node = nodes.new(name=bottle.request.forms.get('name'))
    node.to_ = new_node

@bottle.route('/<filepath:path>')
def static_file(filepath):
    return bottle.static_file(filepath, root='.')

bottle.debug(config.debug)
bottle.run(server=config.server, host='0.0.0.0', port=80, reloader=config.debug)
