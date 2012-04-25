import bottle
import pymongo
import json
from list_data import *

root = nodes.get(name='root')
root['items'] = root.to_

def make_node_rep(node, item_levels=0):
    node_rep = node.copy()
    node_rep['_id'] = node.id_str
    if item_levels:
        node_rep = add_node_rep_items(node, node_rep, item_levels-1)
    return node_rep

def add_node_rep_items(node, node_rep, item_levels=0):
    new_node_rep = node_rep.copy()
    node_items = node.to_
    new_items = []
    for item in node_items:
        item_rep = make_node_rep(item, item_levels)
        new_items.append(item_rep)
    new_node_rep['items'] = new_items
    return new_node_rep

@bottle.get('/')
def index():
    context = {'root': pymongo_to_json(make_node_rep(root, 2))}
    return bottle.jinja2_template('list', context)

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

bottle.debug(True)
bottle.run(port=80, reloader=True)
