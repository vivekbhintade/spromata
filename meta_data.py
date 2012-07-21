import config
from util import *

import pymongo
from bson.objectid import ObjectId as oid
from geventmongo import Pool

# Set up Mongo
mongo_connection = pymongo.Connection(host=config.mongo_host, port=config.mongo_port)
mongo_connection._Pool = Pool
db = mongo_connection[config.mongo_db]

def adj_id(d):
    if d.has_key('_id'):
        if not isinstance(d['_id'], oid):
            d['_id'] = oid(d['_id'])

class Collection(object):
    type = Document
    def fetch(self, **query):
        return [self.type(item) for item in self.collection.find(query)[:]]
    def search(self, **query):
        search_query = {}
        # build regex search from flat query
        for k, v in query.items():
            search_query[k] = {'$regex': '%s' % v, '$options': 'i'}
        return self.fetch(**search_query)
    def get(self, **query):
        adj_id(query)
        found = self.collection.find_one(query)
        if found:
            return self.type(found)
        else:
            return None
    def count(self, **query):
        return self.collection.find(query)[:].count()
    def exists(self, **query):
        return self.count(**query) > 0
    def new(self, **data):
        _id = self.collection.insert(data)
        data['_id'] = _id
        return self.type(data)
    def update(self, **data):
        adj_id(data)
        new_data = data.copy()
        del new_data['_id']
        self.collection.update({'_id': data['_id']}, {'$set': new_data})
        return self.get(_id=data['_id'])
    def remove(self, **data):
        adj_id(data)
        self.collection.remove(data)

