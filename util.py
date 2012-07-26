import bottle
from collections import defaultdict
import hashlib
from functools import partial
import boto
import math
import time
import requests
import json
import bson.json_util
from bson.objectid import ObjectId as oid
import datetime
import string
import random
import urllib2
import urllib
import sys
import os
from spromata.utils.pretty_date import *

import config
def spromata_root(): return os.path.dirname(__file__)
def spromata_static_path(): return os.path.join(spromata_root(), 'static')

from templating import *

def log(s): sys.stderr.write(str(s).strip() + '\n')

def password_hash(s): return hashlib.sha512(s).hexdigest()

def send_mail(to_address, from_address, subject, message_text, message_html):
    print requests.post("https://api.mailgun.net/v2/%s.mailgun.org/messages" % mailgun_api_account, auth=('api', mailgun_api_key), data={
        'to': to_address,
        'from': from_address,
        'subject': subject,
        'text': message_text,
        'html': message_html
    })

def better_default(obj):
    if isinstance(obj, str): return obj
    if isinstance(obj, oid): return str(obj)
    if isinstance(obj, Document): return obj.to_json()
    if hasattr(obj, 'isoformat'): return obj.isoformat()
    if isinstance(obj, list):
        return map(better_default, obj)
    if isinstance(obj, dict):
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
        self_copy['_id'] = self.id_str
        print "TO JSON: %s" % self_copy
        # ensure public keys
        for a in self.public:
            if not self_copy.has_key(a):
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

s3_conn = boto.connect_s3(config.aws_access_key, config.aws_secret_key)
def upload_to_s3(bucket_name, file, filename=None):
    bucket = s3_conn.get_bucket(bucket_name)
    if not filename: filename = file.name
    timestamp = str(time.time())
    file_key = bucket.new_key('.'.join([timestamp, filename]));
    #file_encoded = base64.b64encode(file.read())
    #file_key.set_contents_from_string(file_encoded)
    file_key.set_contents_from_file(file)
    #file_key.make_public()
    return 'http://%s.s3.amazonaws.com/%s' % (bucket.name, file_key.name)
