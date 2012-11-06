from spromata.util import *
from spromata.core.data import *
from spromata.core.auth import *

@bottle.get('/admin')
@require_admin
def admin_dashboard():
    all_users = users.fetch()
    bottle.response.context['all_users'] = all_users
    return render('admin/dashboard')

def filter_dict(d, keys):
    return dict([ (k,v) for k,v in d.items() if k in keys ])

@bottle.put('/admin/users/:user_id')
@require_admin
def update_user(user_id):
    user = users.get(_id=user_id)
    new_user = bottle.request.json
    if user and new_user:
        if new_user.has_key('password'):
            new_user['password'] = password_hash(new_user['password'])
        user.update(new_user)
        users.update(**user)
    return json.dumps(user.to_json())

@bottle.delete('/admin/users/:user_id')
@require_admin
def delete_user(user_id):
    user = users.get(_id=user_id)
    users.remove(_id=user.id)
    return "{}"
