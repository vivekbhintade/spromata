from meta_data import *
import hjklist_config as config

conn = pymongo.Connection(host=config.db_host)
db = conn.nimbus

class User(Document):
    types = {'links': list}
    @property
    def links(self):
        return links.by_user(self)
    @property
    def activated_links(self):
        return links.activated_by_user(self)
    @property
    def remaining_links(self):
        return self.plan.quantity - self.activated_links
    @property
    def has_paid(self):
        return self.has_key('stripe_id')
    @property
    def plan(self):
        if self.has_key('plan'):
            return plans.get(_id=self['plan'])
        else: return FREE_PLAN
    def has_plan(self, plan):
        if self.has_key('plan'): return self.plan.id == plan.id
        else: return not (plan.price > 0)

class Users(Collection):
    collection = db.users
    type = User
    def auth(self, username, password):
        return self.get(username=username, password=password, deactivated={'$exists': False})

class Edge(Document): 
    @property
    def to_(self): return nodes.get(_id=self['to_'])
    @property
    def from_(self): return nodes.get(_id=self['from_'])

class Edges(Collection):
    collection = db.edges
    type = Edge
    def to_(self, node): return self.fetch(to_=node.id)
    def from_(self, node): return self.fetch(from_=node.id)

class Node(Document):
    def __init__(self, *args, **kwargs):
        Document.__init__(self, *args, **kwargs)
        #self['items'] = self.to_
    def get_to_(self): return [e.to_ for e in edges.from_(self)]
    def set_to_(self, other):
        print "Making it..."
        edges.new(from_=self.id, to_=other.id)
        print "Made it..."
    to_ = property(get_to_, set_to_)
    @property
    def from_(self): return [e.from_ for e in edges.to_(self)]

class Nodes(Collection):
    collection = db.nodes
    type = Node

edges = Edges()
nodes = Nodes()

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
    if len(new_items) > 0: new_node_rep['items'] = new_items
    return new_node_rep

