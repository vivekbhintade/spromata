import json
from collections import defaultdict
import pymongo
import pymongo.json_util
from pymongo.objectid import ObjectId as oid
import hjklist_config as config

conn = pymongo.Connection(host=config.db_host)
db = conn.nimbus

class attrdict(defaultdict):
    def __getattr__(self, key): return self[key]
    def __setattr__(self, key, val): self[key]=val

def tree(): return attrdict(tree)

def pymongo_to_json(thing):
    return json.dumps(thing, default=pymongo.json_util.default)

class Document(dict):
    types = {}
    def __getattr__(self, key):
        if self.has_key(key): return self[key]
        else: return None
    #def __setattr__(self, key, val): self[key]=val
    @property
    def id(self):
        return self._id
    @property
    def id_str(self):
        return str(self.id) if self.id else ''
    def to_json(self): return pymongo_to_json(self)

class Collection(object):
    type = Document
    def fetch(self, **query):
        return [self.type(item) for item in self.collection.find(query)]
    def get(self, **query):
        if query.has_key('_id'):
            query['_id'] = oid(query['_id'])
        found = self.collection.find_one(query)
        if found:
            return self.type(found)
        else:
            return None
    def count(self, **query):
        return self.collection.find(query).count()
    def exists(self, **query):
        return self.count(**query) > 0
    def new(self, **data):
        _id = self.collection.insert(data)
        data['_id'] = _id
        return self.type(data)
    def update(self, **data):
        self.collection.update({'_id': data['_id']}, data)
        print "** Update ! ** %s" % str(data)
    def remove(self, **data):
        self.collection.remove(data)

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
