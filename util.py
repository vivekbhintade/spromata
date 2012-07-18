import bottle
from collections import defaultdict
import hashlib
import time
import requests
import json
import bson.json_util
from bson.objectid import ObjectId as oid
import datetime
import string
import random
import sys
import os
from spromata.utils.pretty_date import *

import config
def spromata_root(): return os.path.dirname(__file__)
def spromata_static_path(): return os.path.join(spromata_root(), 'static')

from templating import *

def log(s): sys.stderr.write(str(s).strip() + '\n')

def password_hash(s): return hashlib.sha512(s).hexdigest()

def pymongo_to_json(thing):
    return json.dumps(thing, default=bson.json_util.default)

class Document(dict):
    types = {}
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
            #print "** %s: First time fetch: %s!" % (self, key)
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
    def to_json(self):
        self_copy = self.copy()
        # turn _id into str(id)
        self_copy['id'] = self.id_str
        del self_copy['_id']
        # delete private keys
        for a in self.private:
            if self_copy.has_key(a):
                del self_copy[a]
        # sterilize other fields
        for k, v in self_copy.items():
            if isinstance(v, oid):
                self_copy[k] = str(v)
        return self_copy

class Context(Document): pass

def start_context():
    context = Context()
    context['messages'] = []
    context['errors'] = []
    context['config'] = config
    context['submitted'] = Document()
    context['timestamp'] = time.time()
    return context

def google_image_search(s):
    response = requests.get(
        'https://ajax.googleapis.com/ajax/services/search/images',
        params={'v': '1.0', 'q': s},
        headers={'Referer': 'http://sprobertson.com/'}
    )
    image_url = random.choice(response.json['responseData']['results'])['url']
    return image_url

# Helper for defining routes from a route map
# The map looks like: {'/': index}
# With optional prefixes #post, >put, and Xdelete
# e.g. {'#/login': do_login}
def make_route_callbacks(b, route_map):
    for route in route_map:
        path, callback = route
        print "PATH: %s" % path
        if path.startswith('#'):
            b.post(path[1:])(callback)
        elif path.startswith('X'):
            b.delete(path[1:])(callback)
        elif path.startswith('>'):
            b.put(path[1:])(callback)
        else:
            b.get(path)(callback)
