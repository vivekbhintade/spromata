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

class Results(list): pass

class Collection(object):
    type = Document
    def fetch(self, **query):
        #print "QUERY: %s" % query
        fetch_query = {}
        # build regex search from flat query
        for k, v in query.items():
            # don't add options
            if not k.startswith('_'): fetch_query[k] = v
        if query.has_key('_include'):
            fields = dict([(f, 1) for f in query['_include']])
            results = self.collection.find(fetch_query, fields)
        elif query.has_key('_exclude'):
            fields = dict([(f, 0) for f in query['_exclude']])
            del query['_exclude']
            results = self.collection.find(fetch_query, fields)
        else:
            results = self.collection.find(fetch_query)
        total = results.count()
        if query.has_key('_sort'):
            sort_key = query['_sort']
            sort_dir = 1
            if sort_key.startswith('-'):
                sort_key = sort_key[1:]
                sort_dir = -1
            results = results.sort(sort_key, sort_dir)
        if query.has_key('_skip'): results = results.skip(int(query['_skip']))
        if query.has_key('_limit'): results = results.limit(int(query['_limit']))
        results = Results([self.type(item) for item in results])
        results.total = total
        return results
    def search(self, **query):
        search_query = {}
        # build regex search from flat query
        for k, v in query.items():
            # don't mess up skip or limit
            if not k.startswith('_') and isinstance(v, str): search_query[k] = {'$regex': '%s' % v, '$options': 'i'}
            else: search_query[k] = v
        return self.fetch(**search_query)
    def get(self, **query):
        adj_id(query)
        if query.has_key('_include'):
            fields = dict([(f, 1) for f in query['_include']])
            del query['_include']
            found = self.collection.find_one(query, fields)
        elif query.has_key('_exclude'):
            fields = dict([(f, 0) for f in query['_exclude']])
            del query['_exclude']
            found = self.collection.find_one(query, fields)
        else: 
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
    def update(self, overwrite=False, **data):
        adj_id(data)
        new_data = data.copy()
        del new_data['_id']
        if overwrite: self.collection.update({'_id': data['_id']}, new_data)
        else: self.collection.update({'_id': data['_id']}, {'$set': new_data})
        return self.get(_id=data['_id'])
    def remove(self, **data):
        adj_id(data)
        self.collection.remove(data)

