from spromata.meta_data import *

class User(Document):
    private = ['password']
    @property
    def full_name(self): return ' '.join(filter(None, [self.first_name, self.last_name]))
    @property
    def name(self):
        if self.has_key('name'): return self['name']
        return self.full_name
    @property
    def is_admin(self): return self.type == 'admin'
    def typed(self): return self # TODO: this is just filler right now

class Users(Collection):
    collection = db.users
    private = ['password']
    type = User
    def auth(self, email, password):
        return self.get(email=email, password=password, deactivated={'$exists': False})

from spromata.tokens import generate_token

class Session(Document):
    types = {
        'messages': list
    }
    def add_message(self, text):
        self.messages.append(text)
        sessions.update(**self)
    @property
    def user(self):
        if self.saved.has_key('user'): return self.saved['user']
        else:
            _user = users.get(_id=self['user'])
            self.saved['user'] = _user
            return self.saved['user']

class Sessions(Collection):
    collection = db.sessions
    type = Session

class EmailSignup(Document):
    @property
    def created_at(self): return pretty_date(self.timestamp)

class EmailSignups(Collection):
    collection = db.email_signups
    type = EmailSignup

users = Users()
sessions = Sessions()
email_signups = EmailSignups()

users.collection.ensure_index('username')

