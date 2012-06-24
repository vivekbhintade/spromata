import json
import requests

def merge_dicts(d1, d2):
    return dict(d1.items() + d2.items())

class Source():
    DEFAULT_PARAMS = {}
    @classmethod
    def get_json(cls, url, params={}):
        print "TRYING TO GET %s with %s"% (url, str(params))
        return json.loads(requests.get(url, params=merge_dicts(cls.DEFAULT_PARAMS, params)).content)
    @classmethod
    def get_resource(cls, path, params={}):
        return cls.get_json(cls.make_url(path), params)

class SoundCloud(Source):
    name = 'soundcloud'
    BASE_URL = 'http://api.soundcloud.com/'
    CONSUMER_KEY = 'v9JXSG1dCP4hxUiDSjv5wg'

    DEFAULT_PARAMS = {'consumer_key': CONSUMER_KEY}

    @classmethod
    def make_url(cls, path):
        return cls.BASE_URL + path + '.json'

class Resource(dict):
    type = 'resource'
    types = {}
    sub_resources = {}
    def __getattr__(self, key):
        if self.has_key(key):
            if self.types.has_key(key):
                return self.types[key](self[key])
            return self[key]
        if self.sub_resources.has_key(key):
            sub_type_name = self.sub_resources[key]
            if sub_type_name.startswith('['):
                sub_type_name = sub_type_name.strip('[]')
                sub_type = globals()[sub_type_name]
                sub_type = type(sub_type.__name__+"Collection", (Collection, ), {'sub_type': sub_type, 'name': key.capitalize(), 'id_str': self.make_full_path(self.id, key)})
                #return self.fetch_sub_resource(key, sub_type)
            else:
                sub_type = globals()[sub_type_name]
                #return self.get_sub_resource(key, sub_type)
            return self.get_sub_resource(key, sub_type)
        else: return None
    def to_json(self): return json.dumps(self)
    @classmethod
    def make_path(cls, id, subresource=None):
        path = '%s/%s' % (cls.path_root, id)
        if subresource: path = '%s/%s' % (path, subresource)
        return path
    @classmethod
    def make_full_path(cls, id, subresource=None):
        path = '%s/%s/%s' % (cls.source.name, cls.path_root, id)
        if subresource: path = '%s/%s' % (path, subresource)
        return path
    @property
    def id_str(self): return self.make_full_path(self.id)
    @classmethod
    def get(cls, id):
        return cls(cls.source.get_resource(cls.make_path(id)))
    def get_sub_resource(self, sub_path, sub_type):
        return sub_type(self.source.get_resource(self.make_path(self.id, sub_path)))
    def fetch_sub_resource(self, sub_path, sub_type):
        return [sub_type(i) for i in self.source.get_resource(self.make_path(self.id, sub_path))]
    @classmethod
    def search(cls, **query):
        return [cls(i) for i in cls.source.get_resource(cls.path_root, query)]

class Collection(Resource):
    type = 'collection'
    def __init__(self, items):
        self.items = [self.sub_type(i) for i in items]
    def __getitem__(self, item):
        return self.items.__getitem__(item)
    @property
    def to_(self): return self.items

class User(Resource):
    source = SoundCloud
    path_root = 'users'
    sub_resources = {
        'tracks': '[Track]',
        'favorites': '[Track]',
        'followers': '[User]',
        'followings': '[User]',
        'comments': '[Comment]',
    }
    @property
    def name(self): return self.username
    @property
    def to_(self):
        return [self.tracks, self.favorites, self.followers, self.followings, self.comments]

class Track(Resource):
    source = SoundCloud
    path_root = 'tracks'
    sub_resources = {
        'comments': '[Comment]',
        'favoriters': '[User]',
    }
    @property
    def name(self): return self.title
    @property
    def to_(self):
        return [self.user, self.favoriters, self.comments]

Track.types['user'] = User

class Comment(Resource):
    source = SoundCloud
    @property
    def path_root(self): return
    path_root = 'comments'
    types = {'user': User, 'track': Track}
    @property
    def name(self): return self.body
    @property
    def to_(self):
        return [self.user, self.track]

SoundCloud.resources = {'users': User, 'tracks': Track, 'comments': Comment}

sources = {'soundcloud': SoundCloud}

#me = User.get('929224')
