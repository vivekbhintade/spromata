from bson.objectid import ObjectId as oid
from collections import MutableMapping
import json

def better_default(obj):
    if isinstance(obj, str): return obj
    if isinstance(obj, oid): return str(obj)
    if isinstance(obj, Document): return obj.to_json()
    if hasattr(obj, 'isoformat'): return obj.isoformat()
    if isinstance(obj, list):
        return map(better_default, obj)
    if isinstance(obj, (dict, MutableMapping)):
        return dict([(k, better_default(v)) for k,v in obj.items()])
    #return bson.json_util.default(obj)
    return obj
def old_pymongo_to_json(thing):
    return json.dumps(thing, default=better_default)
def new_pymongo_to_json(thing):
    if hasattr(thing, 'to_json'): thing = thing.to_json()
    thing = better_default(thing)
    return json.dumps(thing)
pymongo_to_json = new_pymongo_to_json

class Document(dict):
    types = {}
    public = []
    private = []
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.saved = {}
    def __getattr__(self, key):
        if self.has_key(key):
            if self.types.has_key(key):
                return self.types[key](self.__getitem__(key))
            return self.__getitem__(key)
        if self.types.has_key(key):
            new_ = self.types[key]()
            self.__setitem__(key, new_)
            return self.__getitem__(key)
        else: return None
    @property
    def id(self):
        return self['_id'] if self.has_key('_id') else None
    @property
    def id_str(self):
        return str(self['_id']) if self.has_key('_id') else ''
    @property
    def created_at(self):
        return self.id.generation_time
    def to_json(self):
        self_copy = self.copy()
        # turn _id into str(id)
        self_copy['_id'] = self.id_str
        #print "TO JSON: %s" % self_copy
        # ensure public keys
        for a in self.public:
            if isinstance(a, tuple):
                self_copy[a[0]] = getattr(self, a[1])
            elif isinstance(a, str):
                self_copy[a] = getattr(self, a)
        # sterilize other fields
        self_copy_clean = {}
        for k, v in self_copy.items():
            self_copy_clean[k] = better_default(v)
        # delete private keys
        for a in self.private:
            if self_copy_clean.has_key(a):
                del self_copy_clean[a]
        return self_copy_clean
    def to_json_str(self):
        return json.dumps(self.to_json(), ensure_ascii=False)


